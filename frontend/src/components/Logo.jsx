export default function Logo({ size = 44 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" className="logo">
      <rect width="32" height="32" rx="7" fill="#123C47" />
      <path d="M10 7h9l5 5v13H10z" fill="none" stroke="#fff" strokeWidth="2" strokeLinejoin="round" />
      <path d="M13.5 18.5l3 3 5-6" fill="none" stroke="#45C4B0" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
