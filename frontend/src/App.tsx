import { useState, type ChangeEvent, type FormEvent } from "react";
import "./App.css";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export default function App() {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [token, setToken] = useState<TokenResponse | null>(null);

  function handlePhoneChange(event: ChangeEvent<HTMLInputElement>) {
    setPhone(event.target.value);
  }

  function handlePasswordChange(event: ChangeEvent<HTMLInputElement>) {
    setPassword(event.target.value);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setIsLoading(true);
    setErrorMessage("");
    setToken(null);

    try {
      const formData = new URLSearchParams();
      formData.set("username", phone);
      formData.set("password", password);

      const response = await fetch("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData: { detail?: string } = await response.json();
        throw new Error(errorData.detail ?? "로그인에 실패했습니다.");
      }

      const data: TokenResponse = await response.json();
      setToken(data);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "로그인 중 오류가 발생했습니다."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <h1 id="login-title">로그인</h1>
        <p className="login-description">전화번호와 비밀번호를 입력해 주세요.</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="phone">전화번호</label>
          <input
            id="phone"
            name="username"
            type="tel"
            autoComplete="username"
            value={phone}
            onChange={handlePhoneChange}
            required
          />

          <label htmlFor="password">비밀번호</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={handlePasswordChange}
            required
          />

          {errorMessage && (
            <p className="login-error" role="alert">
              {errorMessage}
            </p>
          )}

          <button type="submit" disabled={isLoading}>
            {isLoading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        {token && (
          <section className="token-result" aria-live="polite">
            <h2>로그인 성공</h2>
            <p>
              토큰 유형: <code>{token.token_type}</code>
            </p>
            <p>액세스 토큰:</p>
            <code className="access-token">{token.access_token}</code>
          </section>
        )}
      </section>
    </main>
  );
}