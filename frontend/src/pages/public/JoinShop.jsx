import { useState } from 'react'
import AuthLayout from '../../components/AuthLayout'
import TextField from '../../components/TextField'
import { validPhone } from '../../utils/validation'
import './css/Register.css'

//TODO: read these from the invite session (Supabase user metadata) once the invite link is wired up
const invite = { shopName: "your shop", email: "" }

const validate = (form) => {
    const errors = {}

    if (!form.firstName.trim()) errors.firstName = "Enter your first name."
    if (!form.lastName.trim()) errors.lastName = "Enter your last name."
    if (!validPhone(form.phone)) errors.phone = "Enter a 10-digit phone number, including area code."

    return errors
}

//Where invited techs land from their invite email to finish creating their account
function JoinShop() {
    const [form, setForm] = useState({ firstName: "", lastName: "", phone: "" })
    const [attempted, setAttempted] = useState(false)

    const errors = attempted ? validate(form) : {}

    const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

    const handleSubmit = (e) => {
        e.preventDefault()
        setAttempted(true)

        if (Object.keys(validate(form)).length > 0) {
            return
        }

        //TODO: POST to /api/auth/invite/ with the invite session's token
    }

    const pitch = (
        <>
            <h2>Welcome to the team.</h2>
            <p>Once you're set up, clock in at the shop with your PIN and you'll join the queue.</p>
        </>
    )

    return (
        <AuthLayout pitch={pitch}>
            <form className="auth-form" onSubmit={handleSubmit} noValidate>
                <div className="auth-heading">
                    <span className="auth-eyebrow">You're invited</span>
                    <h1>Join {invite.shopName}</h1>
                    <p>Add your details to finish setting up. Your shop will give you a PIN for clocking in.</p>
                </div>

                <TextField
                    id="invite-email"
                    label="Email"
                    type="email"
                    value={invite.email}
                    hint="From your invite. Ask your shop owner if this is wrong."
                    readOnly
                />

                <div className="name-row">
                    <TextField
                        id="first-name"
                        label="First name"
                        autoComplete="given-name"
                        value={form.firstName}
                        onChange={update("firstName")}
                        error={errors.firstName}
                    />
                    <TextField
                        id="last-name"
                        label="Last name"
                        autoComplete="family-name"
                        value={form.lastName}
                        onChange={update("lastName")}
                        error={errors.lastName}
                    />
                </div>

                <TextField
                    id="phone"
                    label="Phone"
                    type="tel"
                    autoComplete="tel"
                    placeholder="(555) 123-4567"
                    value={form.phone}
                    onChange={update("phone")}
                    error={errors.phone}
                />

                <button type="submit" className="auth-submit">Finish setup</button>
            </form>
        </AuthLayout>
    )
}

export default JoinShop
