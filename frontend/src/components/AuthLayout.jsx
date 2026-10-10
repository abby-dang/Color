import SwatchLogo from './SwatchLogo'
import './css/AuthLayout.css'

//Split layout for the signed-out pages: plum brand panel on the left, page content on the right.
//`pitch` is what shows in the brand panel; it's hidden on phones, where the panel shrinks to a header.
function AuthLayout({ pitch, children }) {
    return (
        <div className="auth">
            <section className="auth-brand">
                <div className="auth-logo">
                    <SwatchLogo />
                    <span>Color</span>
                </div>

                <div className="auth-pitch">
                    <div className="auth-pitch-content">{pitch}</div>
                    <div className="swatch-strip" aria-hidden="true">
                        <span style={{ background: "var(--swatch-berry)" }} />
                        <span style={{ background: "var(--swatch-peach)" }} />
                        <span style={{ background: "var(--swatch-nude)" }} />
                        <span style={{ background: "var(--swatch-lilac)" }} />
                        <span style={{ background: "var(--swatch-sage)" }} />
                    </div>
                </div>

                <p className="auth-tagline">Nail Technician Management System</p>
            </section>

            <main className="auth-main">
                {children}
            </main>
        </div>
    )
}

export default AuthLayout
