import { DynamicIcon, type IconName } from "lucide-react/dynamic";

interface DynamicIconProps {
  name: IconName;
  size?: number;
  color?: string;
  className?: string;
}

export default function Icon({
  name,
  size = 20,
  color,
  className = "text-gray-600",
}: DynamicIconProps) {
  return (
    <DynamicIcon
      name={name}
      size={size}
      color={color}
      className={className}
    />
  );
}