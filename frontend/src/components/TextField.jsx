import './css/Fields.css'

//Label + input + optional hint or error. Any other props (type, value, onChange…) go to the <input>.
function TextField({ id, label, labelAction, hint, error, ...inputProps }) {
    const messageId = error || hint ? `${id}-message` : undefined

    return (
        <div className="field">
            <div className="field-row">
                <label htmlFor={id}>{label}</label>
                {labelAction}
            </div>
            <input
                id={id}
                aria-invalid={error ? true : undefined}
                aria-describedby={messageId}
                {...inputProps}
            />
            {error && <FieldMessage id={messageId} error>{error}</FieldMessage>}
            {!error && hint && <FieldMessage id={messageId}>{hint}</FieldMessage>}
        </div>
    )
}

export function FieldMessage({ id, error, children }) {
    return (
        <span id={id} className={error ? "field-message field-message-error" : "field-message"}>
            {error && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="9" />
                    <path d="M12 7.5v5.5" />
                    <path d="M12 16.5v.5" />
                </svg>
            )}
            {children}
        </span>
    )
}

export default TextField
