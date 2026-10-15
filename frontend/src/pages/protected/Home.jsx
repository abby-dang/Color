import NavBar from '../../components/NavBar'
import {useAuth} from '../../context/useAuth'
import {getTimePeriod, toLocalDateString} from '../../utils/date'
import ShopCard from '../../components/ShopCard'
import WorkCard from '../../components/WorkCard'
import {getShopsOwned, getTechAttendanceCount} from '../../api/shopApi'
import {getTechShops} from '../../api/techApi'
import {fetchTodayAppointments} from '../../api/appointmentApi'
import {useState, useEffect} from 'react'
import './css/Home.css'
function Home() {
    const { user } = useAuth()
    const firstName = user?.firstName ? user.firstName : "";
    const timePeriod = getTimePeriod(new Date());
    const [error, setError] = useState(null)
    const [shopsOwned, setShopsOwned] = useState([])
    const [shopsWorkedAt, setShopsWorkedAt] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if(!user) return
        const today = toLocalDateString(new Date())

        //Attach each shop's appointments for today before storing the shops
        getShopsOwned(user.id)
            .then((shops) => Promise.all(
                shops.map((shop) =>
                    fetchTodayAppointments(shop.shop_id, today)
                        .then((appointments) => ({ ...shop, appointments }))
                    
                    )
            ))
            .then((shops) => Promise.all(
                shops.map((shop) =>
                    getTechAttendanceCount(shop.shop_id, today, shop.close_t)
                        .then((techs_clocked_in) => ({ ...shop, techs_clocked_in }))
                )
            ))
            .then(setShopsOwned)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false))
        
       getTechShops()
            .then(setShopsWorkedAt)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false))
    }, [user])

    return(
        <div className="home">
            <NavBar />

            <div className="home-content">
                <h1>Good {timePeriod}, {firstName}</h1>
                <p>Pick a salon to get started.</p>
                <div className="home-shops-container">
                    <p>SALONS YOU OWN</p>
                    {loading ? (
                        <div className="home-loading" role="status">
                            <span className="home-loading__spinner" aria-hidden="true" />
                            <span>Loading your salons…</span>
                        </div>
                    ) : (
                        <div className="home-shops">
                            {shopsOwned.map((shop) => (
                                <ShopCard
                                    key={shop.shop_id}
                                    shop = {shop}
                                />
                            ))}
                            <button type="button" className="home-add-salon">
                                <span className="home-add-salon__icon">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                                        <path d="M12 5v14M5 12h14" />
                                    </svg>
                                </span>
                                Register salon
                            </button>
                        </div>
                    )}
                </div>
                <div className="home-shops-container">
                    <p>WHERE YOU WORK</p>    
                    {loading ? (
                        <div className="home-loading" role="status">
                            <span className="home-loading__spinner" aria-hidden="true" />
                            <span>Loading your salons…</span>
                        </div>
                    ) : shopsWorkedAt.length === 0 ? (
                        <div className="home-work-empty">
                            <span className="home-work-empty__icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                                    <rect x="3" y="5" width="18" height="14" rx="2" />
                                    <path d="M3 7l9 6 9-6" />
                                </svg>
                            </span>
                            <div className="home-work-empty__text">
                                <h3 className="home-work-empty__title">You're not on staff at any salon yet</h3>
                                <p className="home-work-empty__details">When a salon owner adds you as a tech, you'll get an invite by email. Accept it and the salon shows up here.</p>
                            </div>
                        </div>
                    ) : (
                        <div className="home-work">
                            {shopsWorkedAt.map((shop) => (
                                <WorkCard key={shop.shop_id} work={shop} />
                            ))}
                        </div>
                    )}
                </div>
                
            </div>
        </div>
    )
}
export default Home;