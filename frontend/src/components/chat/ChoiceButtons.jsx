export default function ChoiceButtons({ options, onChoice, disabled }) {
  if (!options?.length) return null
  return (
    <div className="choice-buttons">
      {options.map(opt => (
        <button
          key={opt}
          className="btn btn-choice"
          disabled={disabled}
          onClick={() => onChoice(opt)}
        >
          {opt.charAt(0).toUpperCase() + opt.slice(1)}
        </button>
      ))}
    </div>
  )
}
