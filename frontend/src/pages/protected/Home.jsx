import NavBar from '../../components/NavBar'
import {useAuth} from '../../context/useAuth'
import {getTimePeriod, toLocalDateString} from '../../utils/date'
import ShopCard from '../../components/ShopCard'
import {getShopsOwned} from '../../api/shopApi'
import {fetchTodayAppointments} from '../../api/appointmentApi'
import {useState, useEffect} from 'react'
function Home() {
    const { user } = useAuth()
    const firstName = user?.firstName ? user.firstName : "";
    const timePeriod = getTimePeriod(new Date());
    const [error, setError] = useState(null)
    const [shopsOwned, setShopsOwned] = useState([])
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
            .then(setShopsOwned)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false))
    }, [user])

    return(
        <div className="home">
            <NavBar />

            <div className="home-content">
                <h1>Good {timePeriod}, {firstName}</h1>
                <p>Pick a salon to get started.</p>
                <p>SALONS YOU OWN</p>
                {shopsOwned.map((shop) => (
                    <ShopCard
                        key={shop.shop_id}
                        shop = {shop}
                    />
                ))}
                <p>WHERE YOU WORK</p>
            </div>
        </div>
    )
}
export default Home;