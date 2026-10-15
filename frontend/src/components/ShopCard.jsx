import './css/ShopCard.css'
import {convertTimeToRegularFormat} from '../utils/date'
export const ShopCard = ({shop}) => {

    return(
        <div className="shop-card">
            <div className="shop-card__header">
                <h2 className="shop-card__header__title">{shop.name}</h2>
                <div className="shop-card__header__info">
                    <p>{shop.address} · {convertTimeToRegularFormat(shop.open_t)} - {convertTimeToRegularFormat(shop.close_t)   }</p>
                </div>
            </div>      
            <div className="shop-card__body">
                <div className="shop-card__staff">
                    <p>Techs clocked in</p>
                    <p>{shop.techs_clocked_in}</p>
                </div>
                <div className="shop-card__appointments">
                    <p>Appointments today</p>
                    <p>{shop.appointments.length}</p>
                </div>
            </div>
            <div className="shop-card__buttons">
                <button className="shop-card__button">Open dashboard</button>
                <button className="shop-card__button">Open for staff</button>
            </div>
        </div>
    )
}
export default ShopCard