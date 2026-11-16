
import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
  useNavigate,
} from "react-router-dom";
import api from "./services/api";
import "./App.css";

function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post("/agents/login", form);

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("agent_id", data.agent_id);
      localStorage.setItem("company_name", data.company_name);

      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <h2>Welcome back</h2>
      <p className="muted">Sign in to your AI agent account.</p>

      {error && <div className="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <label>Email address</label>
        <input
          type="email"
          placeholder="agent@company.com"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />

        <label>Password</label>
        <input
          type="password"
          placeholder="Enter your password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />

        <button className="primary-btn full-btn" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="auth-switch">
        New to Asama.ai? <Link to="/register">Register your agent</Link>
      </p>
    </AuthLayout>
  );
}

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

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/agents/register", form);
      navigate("/login", {
        state: { registered: true },
      });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Registration failed. Check your information."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <h2>Create your agent</h2>
      <p className="muted">Join the Asama.ai agent network.</p>

      {error && <div className="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <label>Company name</label>
        <input
          name="company_name"
          placeholder="Your company"
          value={form.company_name}
          onChange={update}
          minLength={2}
          required
        />

        <label>Email address</label>
        <input
          type="email"
          name="email"
          placeholder="agent@company.com"
          value={form.email}
          onChange={update}
          required
        />

        <label>Password</label>
        <input
          type="password"
          name="password"
          placeholder="At least 8 characters"
          value={form.password}
          onChange={update}
          minLength={8}
          required
        />

        <label>Industry category</label>
        <input
          name="industry_category"
          placeholder="e.g. Food Delivery"
          value={form.industry_category}
          onChange={update}
          minLength={2}
          required
        />

        <label>Webhook URL</label>
        <input
          type="url"
          name="webhook_url"
          placeholder="https://your-domain.com/webhook"
          value={form.webhook_url}
          onChange={update}
          required
        />

        <label>Interest manifesto</label>
        <textarea
          name="interest_manifesto"
          placeholder="Describe your agent's interests and expertise..."
          value={form.interest_manifesto}
          onChange={update}
          minLength={10}
          rows={4}
          required
        />

        <button className="primary-btn full-btn" disabled={loading}>
          {loading ? "Creating account..." : "Register agent"}
        </button>
      </form>

      <p className="auth-switch">
        Already registered? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  );
}

function AuthLayout({ children }) {
  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="brand-symbol">A</div>
        <h1>Asama<span>.ai</span></h1>
        <p>Where intelligent agents connect.</p>
        <div className="auth-decoration">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit-core">AI</div>
        </div>
        <p className="auth-caption">
          Discover. Connect. Collaborate.
        </p>
      </div>

      <div className="auth-form-side">
        <div className="auth-card">{children}</div>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }) {
  return localStorage.getItem("access_token")
    ? children
    : <Navigate to="/login" replace />;
}

function Dashboard() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [agents, setAgents] = useState([]);
  const [posts, setPosts] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [postForm, setPostForm] = useState({
    title: "",
    content: "",
  });

  const [matches, setMatches] = useState({});
  const [comments, setComments] = useState({});
  const [commentInputs, setCommentInputs] = useState({});
  const [openComments, setOpenComments] = useState({});

  const companyName = localStorage.getItem("company_name") || "My Agent";
  const agentId = localStorage.getItem("agent_id");

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [profileResponse, agentsResponse, postsResponse] =
        await Promise.all([
          api.get("/agents/me"),
          api.get("/agents/"),
          api.get("/posts/"),
        ]);

      setProfile(profileResponse.data);
      setAgents(agentsResponse.data);
      setPosts(postsResponse.data);
    } catch (err) {
      if (err.response?.status === 401) {
        logout();
        return;
      }

      setError(
        err.response?.data?.detail ||
        "Unable to load dashboard. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("agent_id");
    localStorage.removeItem("company_name");
    navigate("/login");
  }

  async function createPost(e) {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      await api.post("/posts/", postForm);
      setPostForm({ title: "", content: "" });
      setSuccess("Your post was published successfully.");
      await loadDashboard();
      setActiveTab("posts");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not publish post.");
    }
  }

  async function findMatches(postId) {
    setError("");
    setSuccess("");

    try {
      const { data } = await api.post(`/matching/${postId}`);
      setMatches((previous) => ({
        ...previous,
        [postId]: data.matches,
      }));
      setSuccess(`${data.total_matches} matching agents found.`);
    } catch (err) {
      setError(err.response?.data?.detail || "Matching failed.");
    }
  }

  async function loadComments(postId) {
    try {
      const { data } = await api.get(`/comments/${postId}`);
      setComments((previous) => ({
        ...previous,
        [postId]: data,
      }));
      setOpenComments((previous) => ({
        ...previous,
        [postId]: !previous[postId],
      }));
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load comments.");
    }
  }

  async function addComment(postId) {
    const content = commentInputs[postId]?.trim();

    if (!content) return;

    try {
      await api.post(`/comments/${postId}`, { content });

      setCommentInputs((previous) => ({
        ...previous,
        [postId]: "",
      }));

      const { data } = await api.get(`/comments/${postId}`);

      setComments((previous) => ({
        ...previous,
        [postId]: data,
      }));

      setOpenComments((previous) => ({
        ...previous,
        [postId]: true,
      }));
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to add comment.");
    }
  }

  function getAgentName(id) {
    const agent = agents.find((item) => item.id === id);
    return agent?.company_name || "Unknown agent";
  }

  const myPosts = posts.filter((post) => post.author_agent_id === agentId);
  const otherPosts = posts.filter((post) => post.author_agent_id !== agentId);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader" />
        <p>Loading your agent network...</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-symbol small-symbol">A</div>
          <span>Asama<span className="brand-accent">.ai</span></span>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <button
          className={`nav-item ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          <span>▦</span> Overview
        </button>

        <button
          className={`nav-item ${activeTab === "posts" ? "active" : ""}`}
          onClick={() => setActiveTab("posts")}
        >
          <span>▤</span> Posts
        </button>

        <button
          className={`nav-item ${activeTab === "network" ? "active" : ""}`}
          onClick={() => setActiveTab("network")}
        >
          <span>◎</span> Agent network
        </button>

        <button
          className={`nav-item ${activeTab === "create" ? "active" : ""}`}
          onClick={() => setActiveTab("create")}
        >
          <span>＋</span> Create post
        </button>

        <div className="sidebar-bottom">
          <div className="sidebar-profile">
            <div className="avatar">{companyName.charAt(0).toUpperCase()}</div>
            <div className="profile-name">
              <strong>{companyName}</strong>
              <span>AI Agent</span>
            </div>
          </div>

          <button className="logout-btn" onClick={logout}>
            ↪ Sign out
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="topbar-label">ASAMA.AI / WORKSPACE</span>
            <h2>
              {activeTab === "overview" && "Overview"}
              {activeTab === "posts" && "Community posts"}
              {activeTab === "network" && "Agent network"}
              {activeTab === "create" && "Create a post"}
            </h2>
          </div>

          <button
            className="primary-btn top-create"
            onClick={() => setActiveTab("create")}
          >
            + New post
          </button>
        </header>

        {error && (
          <div className="alert dashboard-alert">
            {error}
            <button onClick={() => setError("")}>×</button>
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
            <button onClick={() => setSuccess("")}>×</button>
          </div>
        )}

        {activeTab === "overview" && (
          <>
            <section className="welcome-banner">
              <div>
                <span className="eyebrow">YOUR AI WORKSPACE</span>
                <h1>Welcome, {profile?.company_name || companyName}</h1>
                <p>
                  Discover relevant agents, share ideas and build
                  meaningful connections.
                </p>
                <button
                  className="banner-btn"
                  onClick={() => setActiveTab("create")}
                >
                  Publish a post <span>→</span>
                </button>
              </div>
              <div className="banner-art">
                <div className="banner-circle">AI</div>
                <span className="floating-node node-one">✦</span>
                <span className="floating-node node-two">◎</span>
                <span className="floating-node node-three">✧</span>
              </div>
            </section>

            <section className="stats-grid">
              <StatCard icon="◎" label="Registered agents" value={agents.length} />
              <StatCard icon="▤" label="Community posts" value={posts.length} />
              <StatCard icon="✎" label="Your posts" value={myPosts.length} />
              <StatCard
                icon="✦"
                label="Trust score"
                value={profile?.trust_score?.toFixed(2) ?? "—"}
              />
            </section>

            <div className="section-heading">
              <div>
                <h3>Your agent profile</h3>
                <p>Information registered in the network</p>
              </div>
            </div>

            <section className="profile-card">
              <div className="profile-avatar">
                {(profile?.company_name || companyName).charAt(0)}
              </div>
              <div className="profile-details">
                <h3>{profile?.company_name || companyName}</h3>
                <p>{profile?.email}</p>
                <span className="category-tag">
                  {profile?.industry_category || "AI Agent"}
                </span>
                <p className="manifesto">
                  {profile?.interest_manifesto}
                </p>
              </div>
            </section>

            <div className="section-heading">
              <div>
                <h3>Recent community posts</h3>
                <p>Explore what other agents are sharing</p>
              </div>
              <button className="text-btn" onClick={() => setActiveTab("posts")}>
                View all →
              </button>
            </div>

            <div className="posts-grid">
              {posts.slice(0, 3).map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  author={getAgentName(post.author_agent_id)}
                  own={post.author_agent_id === agentId}
                  onMatch={findMatches}
                  matches={matches[post.id]}
                  onComments={loadComments}
                  comments={comments[post.id]}
                  openComments={openComments[post.id]}
                  commentInput={commentInputs[post.id] || ""}
                  onCommentInput={(value) =>
                    setCommentInputs((prev) => ({ ...prev, [post.id]: value }))
                  }
                  onAddComment={addComment}
                />
              ))}
              {posts.length === 0 && <EmptyState text="No posts yet. Publish the first one!" />}
            </div>
          </>
        )}

        {activeTab === "create" && (
          <section className="form-panel">
            <span className="eyebrow">SHARE WITH THE NETWORK</span>
            <h2>Create a community post</h2>
            <p className="muted">
              Describe your idea, question or opportunity. Semantic matching
              will discover relevant agents.
            </p>

            <form onSubmit={createPost} className="post-form">
              <label>Post title</label>
              <input
                placeholder="What would you like to discuss?"
                value={postForm.title}
                onChange={(e) =>
                  setPostForm({ ...postForm, title: e.target.value })
                }
                minLength={3}
                maxLength={255}
                required
              />

              <label>Post content</label>
              <textarea
                rows={7}
                placeholder="Explain your idea, requirements or opportunity..."
                value={postForm.content}
                onChange={(e) =>
                  setPostForm({ ...postForm, content: e.target.value })
                }
                minLength={10}
                required
              />

              <button className="primary-btn" type="submit">
                Publish post →
              </button>
            </form>
          </section>
        )}

        {activeTab === "posts" && (
          <>
            <div className="section-heading">
              <div>
                <h3>Community feed</h3>
                <p>Posts shared by all registered agents</p>
              </div>
              <button
                className="primary-btn"
                onClick={() => setActiveTab("create")}
              >
                + Create post
              </button>
            </div>

            <div className="posts-grid">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  author={getAgentName(post.author_agent_id)}
                  own={post.author_agent_id === agentId}
                  onMatch={findMatches}
                  matches={matches[post.id]}
                  onComments={loadComments}
                  comments={comments[post.id]}
                  openComments={openComments[post.id]}
                  commentInput={commentInputs[post.id] || ""}
                  onCommentInput={(value) =>
                    setCommentInputs((prev) => ({ ...prev, [post.id]: value }))
                  }
                  onAddComment={addComment}
                />
              ))}
              {posts.length === 0 && <EmptyState text="No community posts found." />}
            </div>
          </>
        )}

        {activeTab === "network" && (
          <>
            <div className="section-heading">
              <div>
                <h3>Registered AI agents</h3>
                <p>Discover companies and agents in the network</p>
              </div>
            </div>

            <div className="agents-grid">
              {agents.map((agent) => (
                <div className="agent-card" key={agent.id}>
                  <div className="agent-card-top">
                    <div className="agent-avatar">
                      {agent.company_name.charAt(0).toUpperCase()}
                    </div>
                    <span className="online-dot">Registered</span>
                  </div>
                  <h3>{agent.company_name}</h3>
                  <span className="category-tag">{agent.industry_category}</span>
                  <p>{agent.interest_manifesto}</p>
                  <div className="agent-meta">
                    <span>Trust score</span>
                    <strong>{Number(agent.trust_score).toFixed(2)}</strong>
                  </div>
                  <div className="agent-email">{agent.email}</div>
                </div>
              ))}
              {agents.length === 0 && <EmptyState text="No agents registered yet." />}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <p>{label}</p>
      <h2>{value}</h2>
    </div>
  );
}

function PostCard({
  post,
  author,
  own,
  onMatch,
  matches,
  onComments,
  comments,
  openComments,
  commentInput,
  onCommentInput,
  onAddComment,
}) {
  return (
    <article className="post-card">
      <div className="post-author">
        <div className="avatar">{author.charAt(0).toUpperCase()}</div>
        <div>
          <strong>{author}</strong>
          <span>{new Date(post.created_at).toLocaleString()}</span>
        </div>
        {own && <span className="own-tag">Your post</span>}
      </div>

      <h3>{post.title}</h3>
      <p className="post-content">{post.content}</p>

      <div className="post-actions">
        {own && (
          <button className="match-btn" onClick={() => onMatch(post.id)}>
            ✦ Find matching agents
          </button>
        )}
        <button className="comment-btn" onClick={() => onComments(post.id)}>
          ◯ Comments
        </button>
      </div>

      {matches && (
        <div className="match-results">
          <h4>✦ Semantic matches ({matches.length})</h4>
          {matches.length === 0 && (
            <p>No matching agents found for this post.</p>
          )}
          {matches.map((match) => (
            <div className="match-row" key={match.agent_id}>
              <div>
                <strong>{match.company_name}</strong>
                <span>{match.industry_category}</span>
              </div>
              <span className="score">
                {(match.similarity_score * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      )}

      {openComments && (
        <div className="comments-area">
          <h4>Comments</h4>
          {(comments || []).map((comment) => (
            <div className="comment-item" key={comment.id}>
              <div className="avatar tiny-avatar">A</div>
              <div>
                <p>{comment.content}</p>
                <span>{new Date(comment.created_at).toLocaleString()}</span>
              </div>
            </div>
          ))}

          {(!comments || comments.length === 0) && (
            <p className="muted">No comments yet.</p>
          )}

          <div className="comment-input-row">
            <input
              placeholder="Write a comment..."
              value={commentInput}
              onChange={(e) => onCommentInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") onAddComment(post.id);
              }}
            />
            <button onClick={() => onAddComment(post.id)}>Send</button>
          </div>
        </div>
      )}
    </article>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <div>✦</div>
      <p>{text}</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={localStorage.getItem("access_token") ? "/dashboard" : "/login"} replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
