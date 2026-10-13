import { useState } from 'react'
import { Link } from 'react-router-dom'
import { loginUser } from '../../api/authApi'
import AuthLayout from '../../components/AuthLayout'
import TextField from '../../components/TextField'
import PasswordField from '../../components/PasswordField'
import Alert from '../../components/Alert'
import { useAuth } from '../../context/useAuth'
import { useNavigate } from 'react-router-dom'
function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            const data = await loginUser(email, password)
            if (data.token) {
                login(data)
                navigate("/home")
            } else {
                //Supabase gives no session until the account's email is confirmed
                setError("Please confirm your email before signing in.")
            }
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const pitch = (
        <>
            <h2>Run the floor, not the paperwork.</h2>
            <p>The tech queue, skills, appointments and commissions for your salon — all in one place.</p>
        </>
    )

    return (
        <AuthLayout pitch={pitch}>
            <form className="auth-form" onSubmit={handleSubmit} noValidate>
                <div className="auth-heading">
                    <h1>Sign in</h1>
                    <p>Welcome back. Sign in to manage your shop or join the queue.</p>
                </div>

                {error && (
                    <Alert variant="error" title={error}>
                        Check your email and password and try again.
                    </Alert>
                )}

                <TextField
                    id="email"
                    label="Email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <PasswordField
                    id="password"
                    label="Password"
                    labelAction={<Link to="/forgot-password">Forgot password?</Link>}
                    autoComplete="current-password"
                    placeholder="Your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    invalid={Boolean(error)}
                    required
                />

                <button type="submit" className="auth-submit" disabled={loading}>
                    {loading ? "Signing in…" : "Sign in"}
                </button>

                <div className="auth-divider"><span>or</span></div>

                <p className="auth-switch">New to Color? <Link to="/register">Create an account</Link></p>

                <Alert variant="info">
                    Invited by a shop? Open the link in your invite email to finish setting up your account.
                </Alert>
            </form>
        </AuthLayout>
    )
}

export default Login
