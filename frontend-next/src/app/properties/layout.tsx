export default function PropertiesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-full relative">
      <main>
        {children}
      </main>
    </div>
  );
}
