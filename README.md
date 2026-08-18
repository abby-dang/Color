# Nail Technician Management System (NTMS)

🚧 **Actively in development** — see [Roadmap](#roadmap) below for current status.

A salon management platform in development, aiming to let shop owners manage staff, services, and pricing while giving users a streamlined way to register and interact with a shop. Backend built first; frontend (React) planned next. Built in collaboration with a UX designer.

## Overview

NTMS is designed to solve the operational overhead of running a nail salon — owners need an easy way to manage staff, service offerings, and pricing, while techs need a simple way to register and interact with a shop. The platform is being built around role-based access, so owners, techs, and other users will eventually see different functionality tailored to their needs. A planned core feature is a shared, PIN-accessible queue dashboard for nail techs, receptionists, and owners to view technician priority and skill-based service assignment in real time.

## Tech Stack

- **Backend:** Python / Django
- **Database & Auth:** Supabase (PostgreSQL)
- **API Testing:** Postman
- **Frontend (planned):** React

## Key Features

> **Note:** development so far has been entirely backend-focused. Everything below is implemented and tested via Postman — there is no frontend UI yet.

- **User & shop registration** — end-to-end account creation logic linking authenticated users to shop records
- **Relational database** — 11-table schema supporting secure, role-based data access
- **Backend API** — 8+ endpoints built so far covering authentication and registration logic, tested with Postman as development continues
- **Owner management logic (in progress)** — backend logic for staff management and shop editing across services, staff skill sets, and pricing
- **Role-based access control (in progress)** — shop-level permission checks to distinguish owners, techs, and standard users when accessing a shop

## My Role

I'm the sole developer on this project, working alongside a UX designer who handles visual design. So far, my work has focused entirely on the backend:
- Database schema architecture
- Backend API development (Django) and Supabase authentication integration
- Business logic for registration, role permissions, and owner management features

Frontend implementation (React) is planned next.

## Roadmap

**Done:**
- [x] Database schema design (11 tables)
- [x] User & shop registration flows

**In progress / planned:**
- [ ] Backend API — additional endpoints still being built and tested via Postman (8+ completed so far)
- [ ] Role-based access control (owner, tech, standard user)
- [ ] New tech registration flow
- [ ] Frontend build — React UI for registration, login, and owner dashboard
- [ ] Owner management dashboard — frontend UI implementation
- [ ] Shop PIN-based login for a shared queue dashboard, allowing nail techs, receptionists, and owners to view active queue order, technician priority, and skill-based service matching
- [ ] Appointment booking system

*This project is part of my personal portfolio and is under active development.*
