import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '../../components/AuthLayout'
import TextField from '../../components/TextField'
import PasswordField from '../../components/PasswordField'
import SetupSteps from './SetupSteps'
import {registerUser} from '../../api/authApi'
import { PASSWORD_RULES, validEmail, validPassword, validPhone } from '../../utils/validation'
import './css/Register.css'

const validate = (form) => {
    const errors = {}

    if (!form.firstName.trim()) errors.firstName = "Enter your first name."
    if (!form.lastName.trim()) errors.lastName = "Enter your last name."
    if (!validEmail(form.email)) errors.email = "Enter an email like name@example.com."
    if (!validPhone(form.phone)) errors.phone = "Enter a 10-digit phone number, including area code."
    if (!validPassword(form.password)) errors.password = "Password doesn't meet every rule below."

    return errors
}

function Register() {
    const [form, setForm] = useState({ firstName: "", lastName: "", email: "", phone: "", password: "" })
    //Errors only show after the first submit attempt, then update as the user types
    const [attempted, setAttempted] = useState(false)

    const errors = attempted ? validate(form) : {}

    const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

    const handleSubmit = (e) => {
        e.preventDefault()
        setAttempted(true)

        if (Object.keys(validate(form)).length > 0) {
            return
        }

        registerUser(form.email, form.password, form.firstName, form.lastName, form.phone)
        .then(() => {
            // Navigate to the success page after successful registration
            // Replace this with your actual navigation logic
            window.location.href = "/register/success";
        })
        .catch((error) => {
            // Handle registration error
            console.error("Registration failed:", error);
        });
        //TODO: call registerUser, then navigate("/register/success", { state: { firstName: form.firstName } })
    }

    const pitch = (
        <>
            <h2>Get your salon set up in three steps.</h2>
            <SetupSteps current={1} />
        </>
    )

    return (
        <AuthLayout pitch={pitch}>
            <form className="auth-form auth-form-wide" onSubmit={handleSubmit} noValidate>
                <div className="auth-heading">
                    <h1>Create your account</h1>
                    <p>For salon owners. Techs join through an invite from their shop.</p>
                </div>

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
                    id="email"
                    label="Email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={form.email}
                    onChange={update("email")}
                    error={errors.email}
                />

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

                <PasswordField
                    id="password"
                    label="Password"
                    autoComplete="new-password"
                    value={form.password}
                    onChange={update("password")}
                    invalid={Boolean(errors.password)}
                    describedBy="password-rules"
                >
                    <PasswordRules password={form.password} showMissing={attempted} />
                </PasswordField>

                <button type="submit" className="auth-submit">Create account</button>

                <p className="auth-switch">Already have an account? <Link to="/">Sign in</Link></p>
            </form>
        </AuthLayout>
    )
}

//Live checklist of the backend's password rules. Unmet rules turn red after a submit attempt.
function PasswordRules({ password, showMissing }) {
    return (
        <ul id="password-rules" className="password-rules">
            {PASSWORD_RULES.map((rule) => {
                const met = rule.test(password)
                const state = met ? "met" : showMissing ? "missing" : "pending"

                return (
                    <li key={rule.id} className={`rule rule-${state}`}>
                        <RuleIcon state={state} />
                        {rule.label}
                        <span className="visually-hidden">{met ? " (done)" : " (not yet)"}</span>
                    </li>
                )
            })}
        </ul>
    )
}

function RuleIcon({ state }) {
    if (state === "met") {
        return (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M5 12.5l4.5 4.5L19 7.5" />
            </svg>
        )
    }

    if (state === "missing") {
        return (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
                <path d="M7 7l10 10M17 7L7 17" />
            </svg>
        )
    }

    return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="12" cy="12" r="7" />
        </svg>
    )
}

export default Register
