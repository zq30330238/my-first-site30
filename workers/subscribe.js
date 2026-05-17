export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // GET /subscribers — returns stored emails (for newsletter sender)
    if (url.pathname === '/subscribers' && request.method === 'GET') {
      const auth = request.headers.get('Authorization');
      if (auth !== `Bearer ${env.API_KEY}`) {
        return new Response('Unauthorized', { status: 401 });
      }
      const data = await env.SUBSCRIBERS.get('list');
      return new Response(data || '[]', {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    // POST /subscribe — store new subscriber
    if (url.pathname === '/subscribe' && request.method === 'POST') {
      try {
        const body = await request.json();
        const { email, site } = body;

        if (!email || !email.includes('@') || !email.includes('.')) {
          return new Response(JSON.stringify({ error: 'Invalid email' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
          });
        }

        const now = new Date().toISOString().split('T')[0];
        const raw = await env.SUBSCRIBERS.get('list');
        const subscribers = raw ? JSON.parse(raw) : [];

        const exists = subscribers.find(s => s.email === email && s.site === site);
        if (!exists) {
          subscribers.push({ email, site, joined: now });
          await env.SUBSCRIBERS.put('list', JSON.stringify(subscribers));
        }

        return new Response(JSON.stringify({ success: true, count: subscribers.length }), {
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      } catch (e) {
        return new Response(JSON.stringify({ error: 'Bad request' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
        });
      }
    }

    return new Response('Not found', { status: 404 });
  },
};
