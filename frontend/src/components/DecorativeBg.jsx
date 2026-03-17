export default function DecorativeBg() {
  return (
    <>
      <div className="decor-bg">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
        <div className="blob blob-3" />
        <svg className="connector" preserveAspectRatio="none">
          <path d="M 200,150 Q 400,300 800,200 T 1200,400" />
          <path d="M -100,500 Q 300,600 600,400" />
        </svg>
      </div>
      <div className="floating-shape shape-1" />
      <div className="floating-shape shape-2" style={{ background: 'linear-gradient(135deg, #FDE047, #FACC15)' }} />
    </>
  );
}
