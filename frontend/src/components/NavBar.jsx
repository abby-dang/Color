import SwatchLogo from './SwatchLogo'
import './css/NavBar.css'
import { useAuth } from '../context/useAuth'
function NavBar() {
    const { user } = useAuth()
    const firstInitial = user?.firstName ? user.firstName[0] : "";
    const lastInitial = user?.lastName ? user.lastName[0] : "";
    return(
        <div className="nav-bar">
            <div className = "nav-bar__logo">
                <SwatchLogo />
                <span>Color</span>
            </div>

            <button className="account-menu">
                <span className="account-initials">{firstInitial}{lastInitial}</span>
                <span className="account-name">{user?.firstName ? user.firstName : ""}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M6 9l6 6 6-6" />
                </svg>

            </button>
        </div>
    )
}
export default NavBar;