FROM nginx:alpine

# Copy the static frontend
COPY index.html /usr/share/nginx/html/index.html.template

# Add a script to substitute environment variables in index.html
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-subst-env.sh && \
    echo 'envsubst "\$BACKEND_URL" < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html' >> /docker-entrypoint.d/40-subst-env.sh && \
    chmod +x /docker-entrypoint.d/40-subst-env.sh

EXPOSE 80

# The default nginx entrypoint will run scripts in /docker-entrypoint.d/
CMD ["nginx", "-g", "daemon off;"]
