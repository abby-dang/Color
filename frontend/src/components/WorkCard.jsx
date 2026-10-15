import './css/WorkCard.css'

export const WorkCard = ({work}) => {

    return(
        <div className="work-card">
            <div className="work-card__info">
                <h3 className="work-card__title">{work.name}</h3>
                <p className="work-card__details">{work.attendanceStatus} · {work.rate}% Commission</p>
            </div>

            <button type="button" className="work-card__button">View my day</button>
        </div>
    )
}
export default WorkCard