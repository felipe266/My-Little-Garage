#version 460

in vec2 textureCoord;
in vec3 worldPos;

out vec4 fragColor;

uniform sampler2D imagem;
uniform bool usarLuz;
uniform bool isSombra;
uniform vec3 lightDir;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform vec3 camPos;

// produto escalar (dot)
float calcularIluminacao(vec3 A, vec3 B) {
    return A.x * B.x + A.y * B.y + A.z * B.z;
                
}

// produto vetorial (cross)
vec3 calcularNormal(vec3 A, vec3 B) {
    return vec3(
        A.y * B.z - A.z * B.y,
        A.z * B.x - A.x * B.z,
        A.x * B.y - A.y * B.x
    );
}
void main(){
    vec4 cor = texture(imagem, textureCoord).rgba;

    // desenha a sombra azulada no chao
    if (isSombra) {
        fragColor = vec4(0.06, 0.06, 0.10, 0.45);
        return;
    }

    // sem luz no menu 2D
    if (!usarLuz) {
        fragColor = cor;
        return;
    }

    // acha a normal da face pelas derivadas da tela
    vec3 N = normalize(calcularNormal(dFdx(worldPos), dFdy(worldPos)));

    // garante que a normal aponta pra camera
    vec3 V = normalize(camPos - worldPos);
    if (calcularIluminacao(N, V) < 0.0) {
        N = -N;
    }

    // direcao da luz
    vec3 L = normalize(lightDir);

    // brilho difuso (se tiver de costas fica 0)
    float diff = max(calcularIluminacao(N, L), 0.0);

    // luz ambiente + luz direta do sol
    vec3 iluminacao = ambientColor + lightColor * diff;

    fragColor = vec4(cor.rgb * iluminacao, cor.a);
}
