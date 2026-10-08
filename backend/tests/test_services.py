"""
Unit tests for the backend service layer (nailmanagement/app/services).

Supabase is replaced with an in-memory fake, so these tests never touch the
real database and don't need a .env file. The fake records every query chain
(table, filters, payloads) so tests can assert on what would have been sent.

Run from the backend/ directory:
    venv/Scripts/python -m pytest tests -v

Tests marked xfail document known bugs: they describe the intended behavior
and will start "XPASS"-ing (and fail, because strict=True) once the bug is
fixed, at which point the xfail marker should be removed.
"""
import sys
import types
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import bcrypt
import pytest

# Make "nailmanagement" importable when running pytest from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub the real Supabase client module before any service imports it, so
# importing the services doesn't read .env or create a live client.
_fake_client_module = types.ModuleType("nailmanagement.app.db.supabase_client")
_fake_client_module.supabase = None
sys.modules["nailmanagement.app.db.supabase_client"] = _fake_client_module

from nailmanagement.app.services import appointments as appointments_mod  # noqa: E402
from nailmanagement.app.services import auth as auth_mod  # noqa: E402
from nailmanagement.app.services import clients as clients_mod  # noqa: E402
from nailmanagement.app.services import db_helpers  # noqa: E402
from nailmanagement.app.services import shop_services as shop_services_mod  # noqa: E402
from nailmanagement.app.services import shops as shops_mod  # noqa: E402
from nailmanagement.app.services import skills as skills_mod  # noqa: E402
from nailmanagement.app.services import techs as techs_mod  # noqa: E402
from nailmanagement.app.services import utils  # noqa: E402

SERVICE_MODULES = [
    appointments_mod, auth_mod, clients_mod, db_helpers,
    shop_services_mod, shops_mod, skills_mod, techs_mod,
]

UUID = "11111111-2222-3333-4444-555555555555"
SHOP_ID = 7


# ---------------------------------------------------------------------------
# Fake Supabase
# ---------------------------------------------------------------------------

class FakeQuery:
    """Records a chained query like table().select().eq().execute()."""

    def __init__(self, db, table_name):
        self.db = db
        self.table_name = table_name
        self.calls = []  # [(method, args, kwargs), ...]
        self.executed = False

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        if self.action in ("insert", "upsert"):
            # postgrest-py's insert/upsert builders only support execute()
            raise AttributeError(f"'{name}' can't be chained after {self.action}()")

        def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self

        return method

    def execute(self):
        self.executed = True
        result = self.db._next_result(self.table_name)
        if isinstance(result, Exception):
            raise result
        return SimpleNamespace(data=result)

    def args(self, method):
        """All argument tuples passed to `method` in this chain."""
        return [args for name, args, _ in self.calls if name == method]

    def first(self, method):
        """The first argument passed to `method` (e.g. an insert payload)."""
        return self.args(method)[0][0]

    def has(self, method, *args):
        return args in self.args(method)

    @property
    def action(self):
        for name, _, _ in self.calls:
            if name in ("select", "insert", "upsert", "update", "delete"):
                return name
        return None


class FakeSupabase:
    """
    Stand-in for the supabase Client.

    Queue results per table with `returns(table, *results)`. Each executed
    query on that table pops the next result (a list of rows, or an
    Exception to raise). Tables with nothing queued return [].
    """

    def __init__(self):
        self._results = defaultdict(deque)
        self.queries = []
        self.auth = MagicMock()

    def returns(self, table, *results):
        self._results[table].extend(results)
        return self

    def table(self, name):
        query = FakeQuery(self, name)
        self.queries.append(query)
        return query

    def _next_result(self, table):
        queue = self._results[table]
        return queue.popleft() if queue else []

    def on(self, table, action=None):
        """Queries made against `table`, optionally filtered by action."""
        return [q for q in self.queries
                if q.table_name == table and (action is None or q.action == action)]


@pytest.fixture
def db(monkeypatch):
    fake = FakeSupabase()
    for module in SERVICE_MODULES:
        monkeypatch.setattr(module, "supabase", fake, raising=False)
    return fake


def patch(monkeypatch, module, **attrs):
    """Replace helpers like is_authorized/get_user_id in a module's namespace."""
    for name, value in attrs.items():
        monkeypatch.setattr(module, name, value)


def returns(value):
    return lambda *args, **kwargs: value


def local_to_utc_iso(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").astimezone(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# utils.py
# ---------------------------------------------------------------------------

class TestUtils:
    def test_hash_and_verify_pin_round_trip(self):
        hashed = utils.hash_pin("12345")
        assert hashed != "12345"
        assert utils.verify_pin("12345", hashed)
        assert not utils.verify_pin("54321", hashed)

    @pytest.mark.parametrize("phone, expected", [
        ("5551234567", True),
        ("(555) 123-4567", True),
        ("555.123.4567", True),
        ("555123456", False),
        ("55512345678", False),
        ("", False),
    ])
    def test_valid_phone(self, phone, expected):
        assert utils.valid_phone(phone) is expected

    @pytest.mark.parametrize("email, expected", [
        ("someone@example.com", True),
        ("first.last+tag@sub.example.co", True),
        ("no-at-sign.com", False),
        ("missing@tld", False),
        ("@example.com", False),
    ])
    def test_valid_email(self, email, expected):
        assert bool(utils.valid_email(email)) is expected

    @pytest.mark.parametrize("days, expected", [
        ("m,t,w,th,f", True),
        ("s, sat", True),
        ("", True),
        ("mon,tue", False),
        ("m;t", False),
    ])
    def test_valid_weekdays(self, days, expected):
        assert utils.valid_weekdays(days) is expected

    @pytest.mark.parametrize("password, expected", [
        ("Passw0rd!", True),
        ("Sh0rt!", False),          # too short
        ("password1!", False),      # no uppercase
        ("PASSWORD1!", False),      # no lowercase
        ("Password!!", False),      # no digit
        ("Password12", False),      # no special character
    ])
    def test_valid_password(self, password, expected):
        assert utils.valid_password(password) is expected

    @pytest.mark.parametrize("date_str, expected", [
        ("2026-09-20", True),
        ("09/20/2026", False),
        ("2026-9-20", False),
    ])
    def test_verify_date_format(self, date_str, expected):
        assert utils.verify_date_format(date_str) is expected

    def test_generate_tech_pin_is_four_digits(self):
        for _ in range(50):
            pin = utils.generate_tech_pin()
            assert len(pin) == 4 and pin.isdigit()

    @pytest.mark.parametrize("value", ["14:30", "14:30:00", "14:30:59"])
    def test_convert_time(self, value):
        assert utils.convert_time(value) == "14:30"

    @pytest.mark.parametrize("value", ["2pm", "25:00", ""])
    def test_convert_time_invalid(self, value):
        with pytest.raises(ValueError):
            utils.convert_time(value)

    @pytest.mark.parametrize("value", [
        "2026-09-20", "09/20/2026", "20/09/2026",
        "September 20, 2026", "Sep 20, 2026", "09-20-2026",
    ])
    def test_convert_date(self, value):
        assert utils.convert_date(value) == "2026-09-20"

    def test_convert_date_invalid(self):
        with pytest.raises(ValueError):
            utils.convert_date("not a date")

    def test_convert_date_time(self):
        assert utils.convert_date_time("09/20/2026", "14:30:00") == datetime(2026, 9, 20, 14, 30)


# ---------------------------------------------------------------------------
# db_helpers.py
# ---------------------------------------------------------------------------

class TestDbHelpers:
    def test_get_user_id_found(self, db):
        db.returns("users", [{"user_id": 3}])
        assert db_helpers.get_user_id(UUID) == 3
        assert db.on("users")[0].has("eq", "uuid", UUID)

    def test_get_user_id_not_found(self, db):
        db.returns("users", [])
        assert db_helpers.get_user_id(UUID) == -1

    def test_get_user_id_query_error(self, db):
        db.returns("users", RuntimeError("boom"))
        assert db_helpers.get_user_id(UUID) == -1

    def test_get_owner_id_found(self, db):
        db.returns("shops", [{"owner_id": 3}])
        assert db_helpers.get_owner_id(SHOP_ID) == 3

    def test_get_owner_id_not_found(self, db):
        assert db_helpers.get_owner_id(SHOP_ID) == -1

    def test_is_tech(self, db):
        db.returns("techs", [{"user_id": 3}], [])
        assert db_helpers.is_tech(3, SHOP_ID) is True
        assert db_helpers.is_tech(3, SHOP_ID) is False

    def test_is_user(self, monkeypatch):
        patch(monkeypatch, db_helpers, get_user_id=returns(3))
        assert db_helpers.is_user(UUID) is True
        patch(monkeypatch, db_helpers, get_user_id=returns(-1))
        assert db_helpers.is_user(UUID) is False

    def test_is_owner(self, monkeypatch):
        patch(monkeypatch, db_helpers, get_user_id=returns(3), get_owner_id=returns(3))
        assert db_helpers.is_owner(UUID, SHOP_ID) is True
        patch(monkeypatch, db_helpers, get_owner_id=returns(4))
        assert db_helpers.is_owner(UUID, SHOP_ID) is False

    def test_is_owner_unknown_user_and_shop(self, monkeypatch):
        patch(monkeypatch, db_helpers, get_user_id=returns(-1), get_owner_id=returns(-1))
        assert db_helpers.is_owner(UUID, SHOP_ID) is False

    def test_is_receptionist(self, db, monkeypatch):
        patch(monkeypatch, db_helpers, get_user_id=returns(3))
        db.returns("receptionists", [{"receptionist_id": 1}], [])
        assert db_helpers.is_receptionist(UUID, SHOP_ID) is True
        assert db_helpers.is_receptionist(UUID, SHOP_ID) is False

    @pytest.mark.parametrize("user, owner, receptionist, expected", [
        (True, True, False, True),
        (True, False, True, True),
        (True, False, False, False),
        (False, True, True, False),
    ])
    def test_is_authorized(self, monkeypatch, user, owner, receptionist, expected):
        patch(monkeypatch, db_helpers,
              is_user=returns(user), is_owner=returns(owner), is_receptionist=returns(receptionist))
        assert db_helpers.is_authorized(UUID, SHOP_ID) is expected

    def test_is_client(self, db):
        db.returns("clients", [{"client_id": 5}], [])
        assert db_helpers.is_client(5, SHOP_ID) is True
        assert db_helpers.is_client(5, SHOP_ID) is False
        assert db.on("clients")[0].has("eq", "shop_id", SHOP_ID)


# ---------------------------------------------------------------------------
# clients.py
# ---------------------------------------------------------------------------

@pytest.fixture
def clients_service(db, monkeypatch):
    patch(monkeypatch, clients_mod, is_authorized=returns(True))
    return clients_mod.Clients()


class TestClients:
    def test_create_new_client_inserts_when_email_is_new(self, db, clients_service):
        created = [{"client_id": 1, "email": "a@b.com"}]
        db.returns("clients", [], created)

        result = clients_service.create_new_client(SHOP_ID, "Ann", "Lee", "a@b.com", "5551234567", notes="VIP")

        assert result == created
        insert = db.on("clients", "insert")[0]
        assert insert.first("insert") == {
            "shop_id": SHOP_ID, "first_name": "Ann", "last_name": "Lee",
            "email": "a@b.com", "phone": "5551234567", "notes": "VIP",
        }

    def test_create_new_client_returns_existing_without_insert(self, db, clients_service):
        existing = [{"client_id": 1, "email": "a@b.com"}]
        db.returns("clients", existing)

        assert clients_service.create_new_client(SHOP_ID, "Ann", "Lee", "a@b.com", "5551234567") == existing
        assert db.on("clients", "insert") == []

    def test_get_client_unauthorized(self, db, clients_service, monkeypatch):
        patch(monkeypatch, clients_mod, is_authorized=returns(False))
        with pytest.raises(ValueError, match="not authorized"):
            clients_service.get_client(UUID, SHOP_ID)
        assert db.queries == []

    def test_get_client_applies_filters(self, db, clients_service):
        db.returns("clients", [{"client_id": 1}])

        clients_service.get_client(UUID, SHOP_ID, last_name="le", first_name="an", email="a@b.com", phone="555")

        query = db.on("clients")[0]
        assert query.has("eq", "shop_id", SHOP_ID)
        assert query.has("ilike", "last_name", "%le%")
        assert query.has("ilike", "first_name", "%an%")
        assert query.has("eq", "email", "a@b.com")
        assert query.has("eq", "phone", "555")

    def test_get_client_without_filters_only_scopes_to_shop(self, db, clients_service):
        clients_service.get_client(UUID, SHOP_ID)
        assert db.on("clients")[0].args("eq") == [("shop_id", SHOP_ID)]

    def test_update_client_unauthorized(self, clients_service, monkeypatch):
        patch(monkeypatch, clients_mod, is_authorized=returns(False))
        with pytest.raises(ValueError, match="Unauthorized"):
            clients_service.update_client(UUID, SHOP_ID, 1, first_name="Ann")

    def test_update_client_requires_a_field(self, clients_service):
        with pytest.raises(ValueError, match="No fields"):
            clients_service.update_client(UUID, SHOP_ID, 1)

    def test_update_client_sends_only_given_fields(self, db, clients_service):
        db.returns("clients", [{"client_id": 1}])

        result = clients_service.update_client(UUID, SHOP_ID, 1, phone="5559999999")

        assert result == {"Message": "Client updated successfully"}
        query = db.on("clients", "update")[0]
        assert query.first("update") == {"phone": "5559999999"}
        assert query.has("eq", "shop_id", SHOP_ID)
        assert query.has("eq", "client_id", 1)

    def test_update_client_not_found(self, db, clients_service):
        db.returns("clients", [])
        result = clients_service.update_client(UUID, SHOP_ID, 1, phone="5559999999")
        assert result == {"Message": "Client not found or no changes have been made"}


# ---------------------------------------------------------------------------
# appointments.py
# ---------------------------------------------------------------------------

@pytest.fixture
def appointments_service(db, monkeypatch):
    patch(monkeypatch, appointments_mod, is_authorized=returns(True), is_client=returns(True))
    return appointments_mod.Appointments()


SERVICES = [{"service_id": 1, "tech_id": 4}, {"service_id": 2, "tech_id": 5}]


class TestCreateAppointment:
    def test_rejects_non_client(self, db, appointments_service, monkeypatch):
        patch(monkeypatch, appointments_mod, is_client=returns(False))
        with pytest.raises(Exception, match="not a client"):
            appointments_service.create_appointment(1, SHOP_ID, "", SERVICES)
        assert db.queries == []

    def test_rejects_invalid_status(self, db, appointments_service):
        with pytest.raises(Exception, match="Invalid status"):
            appointments_service.create_appointment(1, SHOP_ID, "", SERVICES, status="done")
        assert db.queries == []

    def test_rejects_invalid_date(self, db, appointments_service):
        with pytest.raises(Exception, match="Invalid date"):
            appointments_service.create_appointment(1, SHOP_ID, "", SERVICES, date="someday", time="10:00")
        assert db.queries == []

    def test_creates_appointment_and_links_services(self, db, appointments_service):
        created = [{"appointment_id": 99}]
        db.returns("appointments", created)

        result = appointments_service.create_appointment(
            1, SHOP_ID, "gel", SERVICES, status="confirmed", date="09/20/2026", time="14:00",
        )

        assert result == created
        assert db.on("appointments", "insert")[0].first("insert") == {
            "client_id": 1,
            "shop_id": SHOP_ID,
            "notes": "gel",
            "datetime": local_to_utc_iso("2026-09-20", "14:00"),
            "status": "confirmed",
        }
        assert db.on("appointment_services", "insert")[0].first("insert") == [
            {"appointment_id": 99, "service_id": 1, "tech_id": 4},
            {"appointment_id": 99, "service_id": 2, "tech_id": 5},
        ]

    def test_defaults_to_pending_now(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])

        appointments_service.create_appointment(1, SHOP_ID, "", SERVICES)

        payload = db.on("appointments", "insert")[0].first("insert")
        assert payload["status"] == "pending"
        stored = datetime.fromisoformat(payload["datetime"])
        assert abs((datetime.now(timezone.utc) - stored).total_seconds()) < 120

    def test_deletes_appointment_when_linking_services_fails(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])
        db.returns("appointment_services", RuntimeError("fk violation"))

        with pytest.raises(Exception, match="fk violation"):
            appointments_service.create_appointment(1, SHOP_ID, "", SERVICES)

        delete = db.on("appointments", "delete")
        assert len(delete) == 1 and delete[0].has("eq", "appointment_id", 99)

    def test_rejects_service_missing_service_id_before_writing(self, db, appointments_service):
        with pytest.raises(Exception, match="service_id"):
            appointments_service.create_appointment(1, SHOP_ID, "", [{"tech_id": 4}])
        assert db.queries == []

    def test_rejects_empty_services_before_writing(self, db, appointments_service):
        with pytest.raises(Exception, match="service_id"):
            appointments_service.create_appointment(1, SHOP_ID, "", [])
        assert db.queries == []

    def test_allows_service_without_tech(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])

        appointments_service.create_appointment(1, SHOP_ID, "", [{"service_id": 1}])

        assert db.on("appointment_services", "insert")[0].first("insert") == [
            {"appointment_id": 99, "service_id": 1, "tech_id": None},
        ]


class TestGetAppointments:
    def test_by_client_unauthorized(self, db, appointments_service, monkeypatch):
        patch(monkeypatch, appointments_mod, is_authorized=returns(False))
        with pytest.raises(ValueError, match="not authorized"):
            appointments_service.get_appointments_by_client(UUID, SHOP_ID, client_id=1)
        assert db.queries == []

    def test_by_client_id(self, db, appointments_service):
        rows = [{"appointment_id": 1}]
        db.returns("appointments", rows)

        assert appointments_service.get_appointments_by_client(UUID, SHOP_ID, client_id=1) == rows
        query = db.on("appointments")[0]
        assert query.has("eq", "shop_id", SHOP_ID)
        assert query.has("eq", "client_id", 1)
        assert query.has("order", "datetime")

    def test_by_client_requires_an_identifier(self, appointments_service):
        with pytest.raises(ValueError, match="Provide a client_id"):
            appointments_service.get_appointments_by_client(UUID, SHOP_ID)

    def test_by_client_name_search_uses_all_matches(self, db, appointments_service, monkeypatch):
        seen = {}

        def fake_get_client(self, uuid, shop_id, **filters):
            seen.update(filters)
            return [{"client_id": 1}, {"client_id": 2}]

        monkeypatch.setattr(clients_mod.Clients, "get_client", fake_get_client)

        appointments_service.get_appointments_by_client(UUID, SHOP_ID, last_name="Lee")

        assert seen["last_name"] == "Lee"
        assert db.on("appointments")[0].has("in_", "client_id", [1, 2])

    def test_by_client_no_matches_returns_empty(self, db, appointments_service, monkeypatch):
        monkeypatch.setattr(clients_mod.Clients, "get_client", returns([]))
        assert appointments_service.get_appointments_by_client(UUID, SHOP_ID, phone="555") == []
        assert not any(q.executed for q in db.on("appointments"))

    def test_by_day_uses_local_day_bounds(self, db, appointments_service):
        appointments_service.get_appointments_by_day(UUID, SHOP_ID, "09/20/2026")

        query = db.on("appointments")[0]
        assert query.has("eq", "shop_id", SHOP_ID)
        assert query.has("gte", "datetime", local_to_utc_iso("2026-09-20", "00:00"))
        assert query.has("lt", "datetime", local_to_utc_iso("2026-09-21", "00:00"))

    def test_by_day_invalid_date(self, appointments_service):
        with pytest.raises(ValueError):
            appointments_service.get_appointments_by_day(UUID, SHOP_ID, "tomorrow")

    def test_by_day_unauthorized(self, appointments_service, monkeypatch):
        patch(monkeypatch, appointments_mod, is_authorized=returns(False))
        with pytest.raises(ValueError, match="not authorized"):
            appointments_service.get_appointments_by_day(UUID, SHOP_ID, "2026-09-20")

    def test_by_tech(self, db, appointments_service):
        appointments_service.get_appointments_by_tech(UUID, SHOP_ID, 4)

        query = db.on("appointment_services")[0]
        assert "appointments!inner(" in query.first("select")
        assert query.has("eq", "tech_id", 4)
        assert query.has("eq", "appointments.shop_id", SHOP_ID)

    def test_get_appointment(self, db, appointments_service):
        rows = [{"appointment_id": 99}]
        db.returns("appointments", rows)
        assert appointments_service.get_appointment(UUID, SHOP_ID, 99) == rows
        assert db.on("appointments")[0].has("eq", "appointment_id", 99)

    def test_get_appointment_is_scoped_to_shop(self, db, appointments_service):
        appointments_service.get_appointment(UUID, SHOP_ID, 99)
        assert db.on("appointments")[0].has("eq", "shop_id", SHOP_ID)


class TestUpdateAppointment:
    def test_unauthorized(self, db, appointments_service, monkeypatch):
        patch(monkeypatch, appointments_mod, is_authorized=returns(False))
        with pytest.raises(ValueError, match="Unauthorized"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x")
        assert db.queries == []

    @pytest.mark.parametrize("kwargs", [{"date": "2026-09-20"}, {"time": "10:00"}])
    def test_requires_date_and_time_together(self, appointments_service, kwargs):
        with pytest.raises(ValueError, match="both date and time"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, **kwargs)

    def test_updates_notes_and_status(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])

        appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="new", status="completed")

        query = db.on("appointments", "update")[0]
        assert query.first("update") == {"notes": "new", "status": "completed"}
        assert query.has("eq", "appointment_id", 99)
        assert db.on("appointment_services") == []

    def test_datetime_is_stored_as_utc_iso_string(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])
        appointments_service.update_appointment(UUID, SHOP_ID, 99, date="2026-09-20", time="14:00")
        payload = db.on("appointments", "update")[0].first("update")
        assert payload["datetime"] == local_to_utc_iso("2026-09-20", "14:00")

    def test_update_is_scoped_to_shop(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])
        appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x")
        assert db.on("appointments", "update")[0].has("eq", "shop_id", SHOP_ID)

    def test_rejects_invalid_status(self, db, appointments_service):
        with pytest.raises(ValueError, match="Invalid status"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, status="done")
        assert db.queries == []

    def test_requires_a_field(self, db, appointments_service):
        with pytest.raises(ValueError, match="No fields"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99)
        assert db.queries == []

    def test_can_clear_notes(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])
        appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="")
        assert db.on("appointments", "update")[0].first("update") == {"notes": ""}

    def test_appointment_in_other_shop_leaves_services_alone(self, db, appointments_service):
        db.returns("appointments", [])  # no row matches this appointment_id + shop_id

        with pytest.raises(ValueError, match="Appointment not found"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x", services=SERVICES)

        assert db.on("appointment_services") == []

    def test_rejects_service_missing_a_key_before_writing(self, db, appointments_service):
        with pytest.raises(ValueError, match="service_id and tech_id"):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x", services=[{"service_id": 1}])
        assert db.queries == []

    def test_replaces_services(self, db, appointments_service):
        old = [{"appointment_id": 99, "service_id": 9, "tech_id": 9}]
        db.returns("appointments", [{"appointment_id": 99}])
        db.returns("appointment_services", old, [], [{"appointment_id": 99}])

        appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x", services=SERVICES)

        actions = [q.action for q in db.on("appointment_services")]
        assert actions == ["select", "delete", "insert"]
        assert db.on("appointment_services", "insert")[0].first("insert") == [
            {"appointment_id": 99, "service_id": 1, "tech_id": 4},
            {"appointment_id": 99, "service_id": 2, "tech_id": 5},
        ]

    def test_services_only_checks_shop_without_empty_update(self, db, appointments_service):
        db.returns("appointments", [{"appointment_id": 99}])

        result = appointments_service.update_appointment(UUID, SHOP_ID, 99, services=SERVICES)

        assert result == [{"appointment_id": 99}]
        assert db.on("appointments", "update") == []
        lookup = db.on("appointments", "select")[0]
        assert lookup.has("eq", "appointment_id", 99) and lookup.has("eq", "shop_id", SHOP_ID)
        assert len(db.on("appointment_services", "insert")) == 1

    def test_restores_old_services_when_insert_fails(self, db, appointments_service):
        old = [{"appointment_id": 99, "service_id": 9, "tech_id": 9}]
        db.returns("appointments", [{"appointment_id": 99}])
        db.returns("appointment_services", old, [], RuntimeError("fk violation"), old)

        with pytest.raises(RuntimeError):
            appointments_service.update_appointment(UUID, SHOP_ID, 99, notes="x", services=SERVICES)

        inserts = db.on("appointment_services", "insert")
        assert len(inserts) == 2
        assert inserts[1].first("insert") == old


# ---------------------------------------------------------------------------
# auth.py
# ---------------------------------------------------------------------------

class TestUserAuthentication:
    @pytest.fixture
    def service(self, db):
        return auth_mod.UserAuthentication()

    def test_sign_up_rejects_bad_phone(self, db, service):
        with pytest.raises(ValueError, match="Phone"):
            service.sign_up("a@b.com", "Ann", "Lee", "123", password="Passw0rd!")
        db.auth.sign_up.assert_not_called()

    def test_sign_up_rejects_weak_password(self, db, service):
        with pytest.raises(ValueError, match="Password"):
            service.sign_up("a@b.com", "Ann", "Lee", "5551234567", password="weak")

    def test_sign_up_requires_password_for_new_users(self, service):
        with pytest.raises(ValueError, match="Password"):
            service.sign_up("a@b.com", "Ann", "Lee", "5551234567")

    def test_sign_up_rejects_bad_email(self, db, service):
        with pytest.raises(ValueError, match="Email"):
            service.sign_up("not-an-email", "Ann", "Lee", "5551234567", password="Passw0rd!")
        db.auth.sign_up.assert_not_called()

    def test_sign_up_creates_auth_user_and_profile(self, db, service):
        db.auth.sign_up.return_value = SimpleNamespace(user=SimpleNamespace(id="new-uuid"))
        db.returns("users", [{"user_id": 1}])

        assert service.sign_up("a@b.com", "Ann", "Lee", "5551234567", password="Passw0rd!") == {"user_id": 1}

        db.auth.sign_up.assert_called_once_with({"email": "a@b.com", "password": "Passw0rd!"})
        assert db.on("users", "insert")[0].first("insert") == {
            "uuid": "new-uuid", "email": "a@b.com", "first_name": "Ann",
            "last_name": "Lee", "phone": "5551234567", "is_active": True,
        }

    def test_sign_up_invited_user_skips_auth(self, db, service):
        db.returns("users", [{"user_id": 1}])
        service.sign_up("a@b.com", "Ann", "Lee", "5551234567", uuid="invited-uuid")
        db.auth.sign_up.assert_not_called()
        assert db.on("users", "insert")[0].first("insert")["uuid"] == "invited-uuid"

    def test_login(self, db, service):
        db.auth.sign_in_with_password.return_value = "session"
        assert service.login("a@b.com", "pw") == "session"
        db.auth.sign_in_with_password.assert_called_once_with({"email": "a@b.com", "password": "pw"})

    def test_login_propagates_errors(self, db, service):
        db.auth.sign_in_with_password.side_effect = RuntimeError("Invalid login credentials")
        with pytest.raises(RuntimeError):
            service.login("a@b.com", "wrong")

    def test_logout(self, db, service):
        assert service.logout() == {"message": "Successfully logged out"}
        db.auth.sign_out.assert_called_once()

    def test_reset_password(self, db, service):
        service.reset_password("a@b.com")
        assert db.auth.reset_password_for_email.call_args.args[0] == "a@b.com"

    def test_update_user_password_rejects_weak(self, db, service):
        with pytest.raises(ValueError):
            service.update_user_password("weak")
        db.auth.update_user.assert_not_called()

    def test_update_user_password(self, db, service):
        service.update_user_password("NewPassw0rd!")
        db.auth.update_user.assert_called_once_with({"password": "NewPassw0rd!"})


# ---------------------------------------------------------------------------
# shop_services.py
# ---------------------------------------------------------------------------

@pytest.fixture
def shop_services_service(db, monkeypatch):
    patch(monkeypatch, shop_services_mod, get_user_id=returns(3), get_owner_id=returns(3))
    return shop_services_mod.Shop_Services()


class TestShopServices:
    @pytest.mark.parametrize("method, args", [
        ("add_service", (UUID, SHOP_ID, "Gel", "desc", 40, 60)),
        ("remove_service", (UUID, SHOP_ID, 1)),
        ("update_service", (UUID, SHOP_ID, 1, "Gel")),
    ])
    def test_owner_only(self, db, shop_services_service, monkeypatch, method, args):
        patch(monkeypatch, shop_services_mod, get_owner_id=returns(4))
        with pytest.raises(ValueError, match="Unauthorized"):
            getattr(shop_services_service, method)(*args)
        assert db.queries == []

    def test_unknown_user(self, shop_services_service, monkeypatch):
        patch(monkeypatch, shop_services_mod, get_user_id=returns(-1))
        with pytest.raises(ValueError, match="User not found"):
            shop_services_service.add_service(UUID, SHOP_ID, "Gel", "desc", 40, 60)

    def test_add_service(self, db, shop_services_service):
        db.returns("shop_services", [{"service_id": 1}])

        assert shop_services_service.add_service(UUID, SHOP_ID, "Gel", "desc", 40, 60) == {"service_id": 1}

        assert db.on("shop_services", "insert")[0].first("insert") == {
            "shop_id": SHOP_ID, "name": "Gel", "description": "desc", "price": 40, "duration": 60,
        }
        assert db.on("shop_service_skills") == []

    def test_add_service_links_skills(self, db, shop_services_service):
        db.returns("shop_services", [{"service_id": 1}])
        db.returns("shop_service_skills", [{"service_id": 1}])

        shop_services_service.add_service(UUID, SHOP_ID, "Gel", "desc", 40, 60, skill_ids=[2, 3])

        assert db.on("shop_service_skills", "insert")[0].first("insert") == [
            {"service_id": 1, "skill_id": 2}, {"service_id": 1, "skill_id": 3},
        ]

    def test_get_shop_services(self, db, shop_services_service):
        rows = [{"name": "Gel"}]
        db.returns("shop_services", rows)
        assert shop_services_service.get_shop_services(SHOP_ID) == rows
        assert db.on("shop_services")[0].has("eq", "shop_id", SHOP_ID)

    def test_remove_service(self, db, shop_services_service):
        db.returns("shop_services", [{"service_id": 1}], [])
        assert shop_services_service.remove_service(UUID, SHOP_ID, 1) == {"Message": "Service removed successfully."}
        assert shop_services_service.remove_service(UUID, SHOP_ID, 1) == {"Message": "Service not found or already removed."}
        query = db.on("shop_services", "delete")[0]
        assert query.has("eq", "shop_id", SHOP_ID) and query.has("eq", "service_id", 1)

    def test_update_service_requires_a_field(self, shop_services_service):
        with pytest.raises(ValueError, match="No fields"):
            shop_services_service.update_service(UUID, SHOP_ID, 1)

    def test_update_service_with_skills(self, db, shop_services_service):
        db.returns("shop_services", [{"service_id": 1}])
        db.returns("shop_service_skills", [], [{"service_id": 1, "skill_id": 2}])

        result = shop_services_service.update_service(UUID, SHOP_ID, 1, price=50, skill_ids=[2])

        assert result == {"Message": "Service updated successfully."}
        assert db.on("shop_services", "update")[0].first("update") == {"price": 50}
        assert [q.action for q in db.on("shop_service_skills")] == ["delete", "insert"]

    def test_update_service_without_skills(self, db, shop_services_service):
        db.returns("shop_services", [{"service_id": 1}])
        assert shop_services_service.update_service(UUID, SHOP_ID, 1, price=50) == {"Message": "Service updated successfully."}


# ---------------------------------------------------------------------------
# shops.py
# ---------------------------------------------------------------------------

SHOP_KWARGS = dict(
    name="Polished", phone="5551234567", pin="12345", address="1 Main St",
    open_t="09:00", close_t="18:00", email="shop@example.com",
    close_d="s", open_d="m,t,w,th,f,sat", uuid=UUID,
)


@pytest.fixture
def shops_service(db, monkeypatch):
    patch(monkeypatch, shops_mod, get_user_id=returns(3), get_owner_id=returns(3), is_tech=returns(False), is_user=returns(True))
    return shops_mod.Shops()


class TestShops:
    @pytest.mark.parametrize("override, message", [
        ({"name": "x" * 101}, "too long"),
        ({"phone": "123"}, "Phone"),
        ({"pin": "1234"}, "PIN"),
        ({"email": "bad"}, "Email"),
        ({"open_d": "m,t,w,th,f,sat,s,x"}, "Invalid input"),
        ({"open_d": "mon"}, "Invalid days"),
    ])
    def test_register_shop_validation(self, db, shops_service, override, message):
        with pytest.raises(ValueError, match=message):
            shops_service.register_shop(**{**SHOP_KWARGS, **override})
        assert db.queries == []

    def test_register_shop_hashes_pin(self, db, shops_service):
        db.returns("shops", [{"shop_id": SHOP_ID}])

        assert shops_service.register_shop(**SHOP_KWARGS) == {"shop_id": SHOP_ID}

        payload = db.on("shops", "insert")[0].first("insert")
        assert payload["owner_id"] == 3
        assert payload["pin"] != "12345"
        assert bcrypt.checkpw(b"12345", payload["pin"].encode())

    def test_register_shop_unknown_user(self, db, shops_service, monkeypatch):
        patch(monkeypatch, shops_mod, get_user_id=returns(-1), is_user=returns(False))
        with pytest.raises(ValueError, match="User not found"):
            shops_service.register_shop(**SHOP_KWARGS)
        assert db.queries == []

    def test_get_owner_shops(self, db, shops_service):
        rows = [{"shop_id": SHOP_ID, "name": "Polished"}]
        db.returns("shops", rows)
        assert shops_service.get_owner_shops(UUID, 3) == rows
        assert db.on("shops")[0].has("eq", "owner_id", 3)

    def test_get_owner_shops_other_owner(self, shops_service):
        with pytest.raises(ValueError, match="Invalid access"):
            shops_service.get_owner_shops(UUID, 4)

    def test_get_shop_info_public(self, db, shops_service):
        db.returns("shops", [{"name": "Polished"}])
        assert shops_service.get_shop_info(SHOP_ID) == {"name": "Polished"}
        assert "owner_id" not in db.on("shops")[0].first("select")

    def test_get_shop_info_owner_sees_private_fields(self, db, shops_service):
        db.returns("shops", [{"shop_id": SHOP_ID, "owner_id": 3}])
        shops_service.get_shop_info(SHOP_ID, uuid=UUID)
        assert "owner_id" in db.on("shops")[0].first("select")

    def test_get_shop_info_tech_sees_private_fields(self, db, shops_service, monkeypatch):
        patch(monkeypatch, shops_mod, get_owner_id=returns(4), is_tech=returns(True))
        db.returns("shops", [{"shop_id": SHOP_ID}])
        shops_service.get_shop_info(SHOP_ID, uuid=UUID)
        assert "owner_id" in db.on("shops")[0].first("select")

    def test_get_shop_info_other_user_gets_public_view(self, db, shops_service, monkeypatch):
        patch(monkeypatch, shops_mod, get_owner_id=returns(4))
        db.returns("shops", [{"name": "Polished"}])
        assert shops_service.get_shop_info(SHOP_ID, uuid=UUID) == {"name": "Polished"}

    def test_get_shop_info_missing_shop(self, db, shops_service):
        with pytest.raises(ValueError, match="Shop not found"):
            shops_service.get_shop_info(SHOP_ID)

    def test_get_shop_commission_total(self, db, shops_service):
        db.returns("commissions", [{"service_amount": "10.50"}, {"service_amount": 4.5}], [])
        assert shops_service.get_shop_commission_total(SHOP_ID, UUID) == 15.0
        assert shops_service.get_shop_commission_total(SHOP_ID, UUID) == 0

    def test_get_shop_commission_total_owner_only(self, shops_service, monkeypatch):
        patch(monkeypatch, shops_mod, get_owner_id=returns(4))
        with pytest.raises(ValueError, match="Invalid Access"):
            shops_service.get_shop_commission_total(SHOP_ID, UUID)

    def test_get_shop_techs_flattens_names(self, db, shops_service):
        db.returns("techs", [{"tech_id": 1, "users": {"first_name": "Kim"}}])
        assert shops_service.get_shop_techs(SHOP_ID) == [{"tech_id": 1, "name": "Kim"}]

    def test_get_shop_skills(self, db, shops_service):
        rows = [{"shop_skill_id": 1, "skills": {"name": "Gel"}}]
        db.returns("shop_skills", rows)
        assert shops_service.get_shop_skills(SHOP_ID) == rows

    def test_add_shop_skill(self, db, shops_service):
        db.returns("shop_skills", [{"shop_skill_id": 1}])
        assert shops_service.add_shop_skill(UUID, SHOP_ID, 2) == {"shop_skill_id": 1}
        assert db.on("shop_skills", "insert")[0].first("insert") == {"shop_id": SHOP_ID, "skill_id": 2}

    def test_remove_shop_skill(self, db, shops_service):
        db.returns("shop_skills", [{"shop_skill_id": 1}])
        assert shops_service.remove_shop_skill(UUID, SHOP_ID, 1) == {"shop_skill_id": 1}
        query = db.on("shop_skills", "delete")[0]
        assert query.has("eq", "shop_id", SHOP_ID) and query.has("eq", "shop_skill_id", 1)

    @pytest.mark.parametrize("method, args", [
        ("add_shop_skill", (UUID, SHOP_ID, 2)),
        ("remove_shop_skill", (UUID, SHOP_ID, 1)),
    ])
    def test_shop_skills_owner_only(self, db, shops_service, monkeypatch, method, args):
        patch(monkeypatch, shops_mod, get_owner_id=returns(4))
        with pytest.raises(ValueError, match="Invalid access"):
            getattr(shops_service, method)(*args)
        assert db.queries == []

    def _update_args(self, pin="12345"):
        return (UUID, SHOP_ID, pin, "New Name", "5551234567", "2 Main St",
                "shop@example.com", "10:00", "19:00", "s", "m,t,w,th,f,sat")

    def test_update_shop_info(self, db, shops_service):
        db.returns("shops", [{"owner_id": 3, "pin": utils.hash_pin("12345")}], [{"shop_id": SHOP_ID}])

        shops_service.update_shop_info(*self._update_args())

        query = db.on("shops", "update")[0]
        assert query.first("update")["name"] == "New Name"
        assert query.has("eq", "shop_id", SHOP_ID)

    def test_update_shop_info_wrong_pin(self, db, shops_service):
        db.returns("shops", [{"owner_id": 3, "pin": utils.hash_pin("12345")}])
        with pytest.raises(ValueError, match="Invalid pin"):
            shops_service.update_shop_info(*self._update_args(pin="99999"))
        assert db.on("shops", "update") == []

    def test_update_shop_info_non_owner(self, db, shops_service):
        db.returns("shops", [{"owner_id": 4, "pin": utils.hash_pin("12345")}])
        with pytest.raises(ValueError, match="Unauthorized"):
            shops_service.update_shop_info(*self._update_args())

    def test_add_new_tech_existing_user(self, db, shops_service, monkeypatch):
        registered = {}
        monkeypatch.setattr(techs_mod.Techs, "register_tech",
                            lambda self, shop_id, user_id, rate: registered.update(shop_id=shop_id, user_id=user_id, rate=rate) or "ok")
        db.returns("users", [{"user_id": 8}])

        assert shops_service.add_new_tech(UUID, SHOP_ID, "tech@example.com", 40) == "ok"
        assert registered == {"shop_id": SHOP_ID, "user_id": 8, "rate": 40}
        db.auth.admin.invite_user_by_email.assert_not_called()

    def test_add_new_tech_invites_new_user(self, db, shops_service):
        db.returns("users", [])

        assert shops_service.add_new_tech(UUID, SHOP_ID, "tech@example.com", 40) == {"Message": "Invitation sent successfully"}

        call = db.auth.admin.invite_user_by_email.call_args
        assert call.args[0] == "tech@example.com"
        assert call.kwargs["options"]["data"] == {"shop_id": SHOP_ID, "commission_rate": 40}

    def test_add_new_tech_owner_only(self, db, shops_service, monkeypatch):
        patch(monkeypatch, shops_mod, get_owner_id=returns(4))
        with pytest.raises(ValueError, match="Invalid access"):
            shops_service.add_new_tech(UUID, SHOP_ID, "tech@example.com", 40)


# ---------------------------------------------------------------------------
# skills.py
# ---------------------------------------------------------------------------

class TestSkills:
    @pytest.fixture
    def service(self, db, monkeypatch):
        patch(monkeypatch, skills_mod, get_user_id=returns(3))
        return skills_mod.Skills()

    def test_add_skill(self, db, service):
        db.returns("skills", [{"skill_id": 1, "name": "Gel"}])
        assert service.add_skill(UUID, "Gel") == {"skill_id": 1, "name": "Gel"}
        assert db.on("skills", "insert")[0].first("insert") == {"name": "Gel"}

    def test_add_skill_unknown_user(self, db, service, monkeypatch):
        patch(monkeypatch, skills_mod, get_user_id=returns(-1))
        with pytest.raises(ValueError, match="User not found"):
            service.add_skill(UUID, "Gel")
        assert db.queries == []

    def test_get_skills(self, db, service):
        rows = [{"skill_id": 1}]
        db.returns("skills", rows)
        assert service.get_skills() == rows

    def test_get_skill_by_name(self, db, service):
        db.returns("skills", [{"skill_id": 1, "name": "Gel"}], [])
        assert service.get_skill_by_name("Gel") == {"skill_id": 1, "name": "Gel"}
        assert service.get_skill_by_name("Nope") is None


# ---------------------------------------------------------------------------
# techs.py
# ---------------------------------------------------------------------------

@pytest.fixture
def techs_service(db, monkeypatch):
    patch(monkeypatch, techs_mod, get_user_id=returns(3), is_tech=returns(True))
    return techs_mod.Techs()


class TestTechs:
    def test_register_tech_skips_existing(self, db, techs_service):
        db.returns("techs", [{"user_id": 3, "shop_id": SHOP_ID}])
        assert techs_service.register_tech(SHOP_ID, 3, 40) is None
        assert db.on("techs", "insert") == []

    def test_register_tech_inserts_with_hashed_pin(self, db, techs_service, monkeypatch):
        patch(monkeypatch, techs_mod, generate_tech_pin=returns("4321"))
        db.returns("techs", [], [{"tech_id": 1}])

        techs_service.register_tech(SHOP_ID, 3, 40)

        payload = db.on("techs", "insert")[0].first("insert")
        assert payload["shop_id"] == SHOP_ID and payload["user_id"] == 3 and payload["commission_rate"] == 40
        assert bcrypt.checkpw(b"4321", payload["pin_hash"].encode())

    @pytest.mark.parametrize("method, args", [
        ("verify_pin", (UUID, SHOP_ID, "1234")),
        ("generate_new_pin", (UUID, SHOP_ID, "1234")),
        ("clock_in_tech", (UUID, SHOP_ID, "1234")),
        ("clock_out_tech", (UUID, SHOP_ID)),
        ("get_tech_attendance", (UUID, SHOP_ID)),
        ("add_tech_skills", (UUID, SHOP_ID, [1])),
        ("remove_tech_skill", (UUID, SHOP_ID, 1)),
    ])
    def test_requires_tech_of_shop(self, db, techs_service, monkeypatch, method, args):
        patch(monkeypatch, techs_mod, is_tech=returns(False))
        with pytest.raises(ValueError, match="not a tech"):
            getattr(techs_service, method)(*args)
        assert db.queries == []

    def test_verify_pin(self, db, techs_service):
        hashed = utils.hash_pin("1234")
        db.returns("techs", [{"pin_hash": hashed}], [{"pin_hash": hashed}])
        assert techs_service.verify_pin(UUID, SHOP_ID, "1234") is True
        assert techs_service.verify_pin(UUID, SHOP_ID, "0000") is False

    def test_verify_pin_without_pin_set(self, db, techs_service):
        db.returns("techs", [{"pin_hash": None}])
        with pytest.raises(ValueError, match="does not have a pin"):
            techs_service.verify_pin(UUID, SHOP_ID, "1234")

    def test_verify_pin_unknown_user(self, techs_service, monkeypatch):
        patch(monkeypatch, techs_mod, get_user_id=returns(-1))
        with pytest.raises(ValueError, match="User not found"):
            techs_service.verify_pin(UUID, SHOP_ID, "1234")

    def test_generate_new_pin(self, db, techs_service):
        old_hash = utils.hash_pin("1234")
        db.returns("techs", [{"pin_hash": old_hash}], [{"tech_id": 1}])

        techs_service.generate_new_pin(UUID, SHOP_ID, current_pin="1234")

        update = db.on("techs", "update")[0]
        assert update.first("update")["pin_hash"] != old_hash
        assert update.has("eq", "user_id", 3) and update.has("eq", "shop_id", SHOP_ID)

    def test_generate_new_pin_wrong_current_pin(self, db, techs_service):
        db.returns("techs", [{"pin_hash": utils.hash_pin("1234")}])
        with pytest.raises(ValueError, match="incorrect"):
            techs_service.generate_new_pin(UUID, SHOP_ID, current_pin="0000")
        assert db.on("techs", "update") == []

    def test_generate_new_pin_first_time_needs_no_current_pin(self, db, techs_service):
        db.returns("techs", [{"pin_hash": None}])
        techs_service.generate_new_pin(UUID, SHOP_ID)
        assert len(db.on("techs", "update")) == 1

    def test_get_tech_shops(self, db, techs_service):
        rows = [{"shop_id": SHOP_ID, "commission_rate": 40, "shops": {"name": "Polished"}}]
        db.returns("techs", rows, [])
        assert techs_service.get_tech_shops(UUID) == rows
        assert techs_service.get_tech_shops(UUID) == []

    def test_clock_in_tech(self, db, techs_service):
        db.returns("techs", [{"pin_hash": utils.hash_pin("1234"), "tech_id": 1}])
        techs_service.clock_in_tech(UUID, SHOP_ID, "1234")
        payload = db.on("tech_attendance", "insert")[0].first("insert")
        assert payload["tech_id"] == 1 and payload["shop_id"] == SHOP_ID

    def test_clock_in_tech_wrong_pin(self, db, techs_service):
        db.returns("techs", [{"pin_hash": utils.hash_pin("1234"), "tech_id": 1}])
        with pytest.raises(ValueError):
            techs_service.clock_in_tech(UUID, SHOP_ID, "0000")
        assert db.on("tech_attendance") == []

    def test_clock_out_tech(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        db.returns("tech_attendance", [{"attendance_id": 50}], [{"attendance_id": 50}])
        techs_service.clock_out_tech(UUID, SHOP_ID)
        assert db.on("tech_attendance", "update")[0].has("eq", "attendance_id", 50)

    def test_clock_out_tech_without_check_in(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        db.returns("tech_attendance", [])
        with pytest.raises(ValueError, match="No active check-in"):
            techs_service.clock_out_tech(UUID, SHOP_ID)

    def test_get_tech_attendance_for_date(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        db.returns("tech_attendance", [{"attendance_id": 50}])

        assert techs_service.get_tech_attendance(UUID, SHOP_ID, "2026-09-20") == [{"attendance_id": 50}]

        query = db.on("tech_attendance")[0]
        assert query.has("gte", "check_in", "2026-09-20T00:00:00Z")
        assert query.has("lte", "check_in", "2026-09-20T23:59:59Z")

    def test_get_tech_attendance_defaults_to_today_utc(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        techs_service.get_tech_attendance(UUID, SHOP_ID)
        today = datetime.now(timezone.utc).date().isoformat()
        assert db.on("tech_attendance")[0].has("gte", "check_in", f"{today}T00:00:00Z")

    def test_get_tech_attendance_bad_date(self, db, techs_service):
        with pytest.raises(ValueError, match="Date format"):
            techs_service.get_tech_attendance(UUID, SHOP_ID, "09/20/2026")

    def test_add_tech_skills(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        techs_service.add_tech_skills(UUID, SHOP_ID, [2, 3])
        assert db.on("tech_skills", "insert")[0].first("insert") == [
            {"tech_id": 1, "skill_id": 2}, {"tech_id": 1, "skill_id": 3},
        ]

    def test_remove_tech_skill(self, db, techs_service):
        db.returns("techs", [{"tech_id": 1}])
        techs_service.remove_tech_skill(UUID, SHOP_ID, 2)
        query = db.on("tech_skills", "delete")[0]
        assert query.has("eq", "tech_id", 1) and query.has("eq", "skill_id", 2)

    def test_get_tech_profile(self, db, techs_service):
        profile = {"first_name": "Kim", "last_name": "Ng", "email": "k@n.com", "phone": "5551234567"}
        db.returns("techs", [{"users": profile}])
        assert techs_service.get_tech_profile(1) == profile

    def test_get_tech_profile_not_found(self, db, techs_service):
        with pytest.raises(IndexError):
            techs_service.get_tech_profile(1)
