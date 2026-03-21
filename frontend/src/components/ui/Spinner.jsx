export default function Spinner({ size = 32, color = 'var(--accent)' }) {
  return (
    <svg
      width={size} height={size}
      viewBox="0 0 50 50"
      className="spinner"
      aria-label="Loading…"
      role="status"
    >
      <circle
        cx="25" cy="25" r="20"
        fill="none"
        stroke={color}
        strokeWidth="4"
        strokeLinecap="round"
        strokeDasharray="80 40"
      />
    </svg>
  )
}
