interface UserAvatarProps {
  initials: string;
  size?: number;
}

export default function UserAvatar({ initials, size = 36 }: UserAvatarProps) {
  return (
    <div
      style={{ width: size, height: size }}
      className="rounded-full bg-grad-primary flex items-center justify-center text-white text-sm font-medium font-display shrink-0"
    >
      {initials}
    </div>
  );
}
