import './css/Alert.css'

//variant: "error" (red banner, announced to screen readers) or "info" (soft tinted note)
function Alert({ variant = "info", title, children }) {
    const isError = variant === "error"

    return (
        <div className={`alert alert-${variant}`} role={isError ? "alert" : undefined}>
            {isError ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="9" />
                    <path d="M12 7v6" />
                    <path d="M12 16.5v.5" />
                </svg>
            ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="3" y="5" width="18" height="14" rx="2" />
                    <path d="m3 7 9 6 9-6" />
                </svg>
            )}
            <div className="alert-body">
                {title && <strong>{title}</strong>}
                <span>{children}</span>
            </div>
        </div>
    )
}

export default Alert
