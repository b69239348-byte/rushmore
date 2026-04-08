interface CategoryHeaderProps {
  title: string;
  subtitle: string;
}

export function CategoryHeader({ title, subtitle }: CategoryHeaderProps) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-black tracking-tight sm:text-3xl">
        {title}
      </h1>
      <p className="mt-1 text-sm text-text-secondary">{subtitle}</p>
    </div>
  );
}
