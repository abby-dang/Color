function SwatchLogo({ size = 34 }) {
    return (
        <svg width={size} height={size} viewBox="0 0 34 34" aria-hidden="true" className="logo-mark">
            <g transform="translate(17 27)">
                <path d="M-5 0V-14a5 8 0 0 1 10 0V0z" transform="rotate(-24)" fill="var(--swatch-lilac)" />
                <path d="M-5 0V-14a5 8 0 0 1 10 0V0z" transform="rotate(24)" fill="var(--swatch-peach)" />
                <path d="M-5 0V-16a5 8 0 0 1 10 0V0z" fill="var(--swatch-berry)" />
            </g>
        </svg>
    )
}

export default SwatchLogo
