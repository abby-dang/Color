export const getTimePeriod = (date) => {
    const hours = date.getHours();
    
    if (hours < 12) {
        return "morning";
    } else if (hours < 18) {
        return "afternoon";
    } else {
        return "evening";
    }

};

//Formats a date as "YYYY-MM-DD" in local time (toISOString would use UTC and can be off by a day)
export const toLocalDateString = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
};