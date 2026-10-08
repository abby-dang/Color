import { useState } from 'react'
import { Link } from 'react-router-dom'
import { loginUser } from '../../api/authApi'
import './css/Login.css'

function SwatchLogo({ size = 34 }) {
    return (
        <svg width={size} height={size} viewBox="0 0 34 34" aria-hidden="true" className="logo-mark">
            <g transform="translate(17 27)">
                <path d="M-5 0V-14a5 8 0 0 1 10 0V0z" transform="rotate(-24)" fill="#9C7BD8" />
                <path d="M-5 0V-14a5 8 0 0 1 10 0V0z" transform="rotate(24)" fill="#F2A07B" />
                <path d="M-5 0V-16a5 8 0 0 1 10 0V0z" fill="#E04A7A" />
            </g>
        </svg>
    )
}

function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState(false)
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            const data = await loginUser(email, password)
            if (data.token) {
                localStorage.setItem("token", data.token)
            }
            //TODO: redirect to the owner's shops once that page exists
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login">
            <section className="login-brand">
                <div className="login-logo">
                    <SwatchLogo />
                    <span>Color</span>
                </div>

                <div className="login-pitch">
                    <h2>Run the floor, not the paperwork.</h2>
                    <p>The tech queue, skills, appointments and commissions for your salon — all in one place.</p>
                    <div className="swatch-strip" aria-hidden="true">
                        <span style={{ background: "#E04A7A" }} />
                        <span style={{ background: "#F2A07B" }} />
                        <span style={{ background: "#F4D6C8" }} />
                        <span style={{ background: "#9C7BD8" }} />
                        <span style={{ background: "#5BA7A0" }} />
                    </div>
                </div>

                <p className="login-tagline">Nail Technician Management System</p>
            </section>

            <main className="login-main">
                <form className="login-form" onSubmit={handleSubmit} noValidate>
                    <div className="login-heading">
                        <h1>Sign in</h1>
                        <p>Welcome back. Sign in to manage your shop or join the queue.</p>
                    </div>

                    {error && (
                        <div className="login-error" role="alert">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                <circle cx="12" cy="12" r="9" />
                                <path d="M12 7v6" />
                                <path d="M12 16.5v.5" />
                            </svg>
                            <div>
                                <strong>{error}</strong>
                                <span>Check your email and password and try again.</span>
                            </div>
                        </div>
                    )}

                    <div className="field">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            autoComplete="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="field">
                        <div className="field-row">
                            <label htmlFor="password">Password</label>
                            <Link to="/forgot-password">Forgot password?</Link>
                        </div>
                        <div className="password-wrap">
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                autoComplete="current-password"
                                placeholder="Your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                aria-invalid={error ? true : undefined}
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                aria-label={showPassword ? "Hide password" : "Show password"}
                                aria-pressed={showPassword}
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
                                    <circle cx="12" cy="12" r="3" />
                                    {showPassword && <path d="M4 4l16 16" />}
                                </svg>
                            </button>
                        </div>
                    </div>

                    <button type="submit" className="login-submit" disabled={loading}>
                        {loading ? "Signing in…" : "Sign in"}
                    </button>

                    <div className="login-divider"><span>or</span></div>

                    <p className="login-register">New to Color? <Link to="/register">Create an account</Link></p>

                    <div className="login-invite">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <rect x="3" y="5" width="18" height="14" rx="2" />
                            <path d="m3 7 9 6 9-6" />
                        </svg>
                        <span>Invited by a shop? Open the link in your invite email to finish setting up your account.</span>
                    </div>
                </form>
            </main>
        </div>
    )
}

export default Login
