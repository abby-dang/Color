import SwatchLogo from './SwatchLogo'
import './css/NavBar.css'
import { useAuth } from '../context/useAuth'
function NavBar() {
    const { user } = useAuth()
    const firstInitial = user?.first_name ? user.first_name[0] : "";
    const lastInitial = user?.last_name ? user.last_name[0] : "";
    return(
        <div className="nav-bar">
            <div className = "auth-logo">
                <SwatchLogo />
                <span>Color</span>
            </div>

            <button className="account-menu">
                <text className="account-initials">{firstInitial}{lastInitial}</text>
                <text className="account-name">{user?.first_name ? user.first_name : ""}</text>
                <svg></svg>
            </button>
        </div>
    )
}
export default NavBar;