import { Link, useLocation } from 'react-router-dom'
import AuthLayout from '../../components/AuthLayout'
import SetupSteps from './SetupSteps'
import './css/Register.css'

function RegisterSuccess() {
    //Register passes the first name along when it navigates here
    const firstName = useLocation().state?.firstName

    const pitch = (
        <>
            <h2>Get your salon set up in three steps.</h2>
            <SetupSteps current={2} />
        </>
    )

    return (
        <AuthLayout pitch={pitch}>
            <div className="auth-form">
                <div className="success-icon">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M5 12.5l4.5 4.5L19 7.5" />
                    </svg>
                </div>

                <div className="auth-heading">
                    <h1>{firstName ? `You're all set, ${firstName}` : "You're all set"}</h1>
                    <p>Your account is ready. Sign in to register your salon. If we sent you a confirmation email, open the link in it first.</p>
                </div>

                <div className="next-card">
                    <span className="auth-eyebrow">Up next</span>
                    <SetupSteps current={2} from={2} variant="card" />
                </div>

                <Link to="/" className="auth-submit">Sign in</Link>
            </div>
        </AuthLayout>
    )
}

export default RegisterSuccess
