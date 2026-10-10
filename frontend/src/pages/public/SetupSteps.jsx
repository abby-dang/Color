const STEPS = [
    { title: "Create your account", detail: "Name, email, phone and a password." },
    { title: "Register your salon", detail: "Hours, address and a shop PIN." },
    { title: "Invite your techs", detail: "They get an email to join your shop." },
]

//The owner's three setup steps. `current` (1–3) is highlighted; `variant="card"` is the light version.
function SetupSteps({ current, from = 1, variant = "panel" }) {
    return (
        <ol className={`setup-steps setup-steps-${variant}`}>
            {STEPS.map((step, index) => {
                const number = index + 1
                if (number < from) return null

                return (
                    <li key={step.title} className={number === current ? "step step-current" : "step"}>
                        <span className="step-number">{number}</span>
                        <div className="step-text">
                            <strong>{step.title}</strong>
                            {variant === "panel" && <span>{step.detail}</span>}
                        </div>
                    </li>
                )
            })}
        </ol>
    )
}

export default SetupSteps
