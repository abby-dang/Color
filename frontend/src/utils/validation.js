//Mirrors the backend checks in backend/nailmanagement/app/services/utils.py so the form
//can catch problems before the request is sent. The server still validates everything.

export const PASSWORD_RULES = [
    { id: "length", label: "8+ characters", test: (pw) => pw.length >= 8 },
    { id: "upper", label: "Uppercase letter", test: (pw) => /[A-Z]/.test(pw) },
    { id: "lower", label: "Lowercase letter", test: (pw) => /[a-z]/.test(pw) },
    { id: "number", label: "Number", test: (pw) => /\d/.test(pw) },
    { id: "symbol", label: "Symbol, like ! or #", test: (pw) => /[^a-zA-Z0-9]/.test(pw) },
]

export const validPassword = (password) => PASSWORD_RULES.every((rule) => rule.test(password))

//Same as valid_phone: 10 digits once punctuation and spaces are stripped
export const validPhone = (phone) => phone.replace(/\D/g, "").length === 10

//Same pattern as valid_email
export const validEmail = (email) => /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
