interface InputFieldProps {
  label: string;
  type: 'text' | 'date' | 'time';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function InputField({ label, type, value, onChange, placeholder }: InputFieldProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder-gray-500"
      />
    </div>
  );
}