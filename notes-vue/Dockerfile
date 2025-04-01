# 第一阶段：构建 Vue.js 项目
FROM node:18-alpine as build-stage

WORKDIR /app
COPY . /app
RUN npm install
RUN npm run build
CMD ["npm", "run", "serve"]

## 第二阶段：使用 Nginx 服务静态文件
#FROM nginx:stable-alpine
#
#COPY --from=build-stage /app/dist /usr/share/nginx/html
#COPY nginx.conf /etc/nginx/conf.d/default.conf
#EXPOSE 80
#
## Nginx 默认会在后台运行，使用这个命令让它在前台运行，以便 Docker 可以跟踪进程
#CMD ["nginx", "-g", "daemon off;"]