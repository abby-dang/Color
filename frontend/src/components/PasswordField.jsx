import { useState } from 'react'
import './css/Fields.css'

//Password input with a show/hide button. `children` renders under the input (e.g. a rules checklist).
function PasswordField({ id, label, labelAction, invalid, describedBy, children, ...inputProps }) {
    const [visible, setVisible] = useState(false)

    return (
        <div className="field">
            <div className="field-row">
                <label htmlFor={id}>{label}</label>
                {labelAction}
            </div>
            <div className="password-wrap">
                <input
                    id={id}
                    type={visible ? "text" : "password"}
                    aria-invalid={invalid ? true : undefined}
                    aria-describedby={describedBy}
                    {...inputProps}
                />
                <button
                    type="button"
                    className="password-toggle"
                    aria-label={visible ? "Hide password" : "Show password"}
                    aria-pressed={visible}
                    onClick={() => setVisible(!visible)}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
                        <circle cx="12" cy="12" r="3" />
                        {visible && <path d="M4 4l16 16" />}
                    </svg>
                </button>
            </div>
            {children}
        </div>
    )
}

export default PasswordField
