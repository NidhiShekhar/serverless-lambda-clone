# docker/javascript/Dockerfile
FROM node:16-alpine

WORKDIR /app

# Set up a non-root user for better security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

COPY function.js /app/
CMD ["node", "function.js"]