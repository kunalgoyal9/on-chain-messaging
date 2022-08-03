import EncryptMessage from "./EncryptMessage";
import DecryptMessage from "./DecryptMessage";

export default function App() {
  return (
    <div className="flex flex-wrap">
      <div className="w-full lg:w-1/2">
        <EncryptMessage />
      </div>
      <div className="w-full lg:w-1/2">
        <DecryptMessage />
      </div>
    </div>
  );
}
