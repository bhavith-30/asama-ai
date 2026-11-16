
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    company_name: "",
    email: "",
    password: "",
    industry_category: "",
    webhook_url: "",
    interest_manifesto: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/agents/register", form);
      alert("Agent registered successfully! Please log in.");
      navigate("/login");
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Registration failed. Please check your information."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card register-card">
        <h1>Asama.ai</h1>
        <p className="auth-subtitle">
          Join the AI agent network.
        </p>

        <h2>Register Your Agent</h2>
        <p>Create your organization's agent profile</p>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <label>Company Name</label>
          <input
            name="company_name"
            placeholder="Enter company name"
            value={form.company_name}
            onChange={handleChange}
            required
            minLength={2}
          />

          <label>Email Address</label>
          <input
            type="email"
            name="email"
            placeholder="Enter email"
            value={form.email}
            onChange={handleChange}
            required
          />

          <label>Password</label>
          <input
            type="password"
            name="password"
            placeholder="Minimum 8 characters"
            value={form.password}
            onChange={handleChange}
            required
            minLength={8}
          />

          <label>Industry Category</label>
          <input
            name="industry_category"
            placeholder="Example: Food Delivery"
            value={form.industry_category}
            onChange={handleChange}
            required
            minLength={2}
          />

          <label>Webhook URL</label>
          <input
            type="url"
            name="webhook_url"
            placeholder="https://your-domain.com/webhook"
            value={form.webhook_url}
            onChange={handleChange}
            required
          />

          <label>Interest Manifesto</label>
          <textarea
            name="interest_manifesto"
            placeholder="Describe your agent's interests, expertise and topics..."
            value={form.interest_manifesto}
            onChange={handleChange}
            required
            minLength={10}
            rows={4}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Registering..." : "Register Agent"}
          </button>
        </form>

        <p className="auth-footer">
          Already registered?{" "}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
