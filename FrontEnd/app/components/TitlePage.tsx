interface TitlePageProps {
  title: string;
  subtitle?: string;
  gradient?: string;
}

export default function TitlePage({
  title,
  gradient = 'from-indigo-500 via-purple-500 to-pink-500'
}: TitlePageProps) {
  return (
    <div className={`group relative overflow-hidden rounded-xl shadow-lg bg-gradient-to-r ${gradient} p-8`}>
      {/* Fondo con patrón */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="gradHeader"%3E%3Cstop offset="0%25" style="stop-color:rgba(241, 99, 227, 0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(4, 6, 105, 0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23gradHeader)"%3E%3C/rect%3E%3C/svg%3E")',
          backgroundSize: '100px 100px',
          backgroundRepeat: 'repeat'
        }}
      />

      {/* Overlay oscuro */}
      <div className="absolute inset-0 bg-black opacity-30" />

      {/* Contenido */}
      <div className="relative">
        <h1 className="text-4xl font-bold text-white">{title}</h1>
      </div>

      {/* Efecto de brillo */}
      <div className="absolute -inset-1 bg-gradient-to-r from-white via-transparent to-white opacity-0 group-hover:opacity-10 blur-xl transition-opacity pointer-events-none" />
    </div>
  );
}
