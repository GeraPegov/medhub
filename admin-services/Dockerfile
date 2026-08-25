FROM golang:1.26.2-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -o /admin ./cmd

FROM alpine:3.23 
WORKDIR /app
COPY --from=builder /admin ./admin

EXPOSE 8001

CMD ["./admin"]
