#version 460

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 texCoord;

uniform mat4 modelMatrix;
uniform mat4 projMatrix;
uniform mat4 camMatrix;

out vec2 textureCoord;
out vec3 worldPos;

void main(){
    vec4 posMundo = modelMatrix * vec4(a_pos, 1.0);
    worldPos = posMundo.xyz;
    gl_Position = projMatrix * camMatrix * posMundo;
    textureCoord = texCoord;
}
