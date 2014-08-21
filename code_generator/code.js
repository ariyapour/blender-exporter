function shade(env) {
    var distance = vronoiNoise(env.texcoord, env.scale);
    var fresnel = fresnelequation(env.blend, env.normal, env.position);
    var eta = calculateEta(env.blend);
    return new Shade().refract(env.normal, eta, 1 - fresnel).reflect(env.normal, fresnel);
}
function calculateEta(blend) {
    return Math.max(1 - blend, 0.00001);
}
function fresnelequation(blend, normal, position) {
    var N = normal.normalize();
    var I = Space.transformDirection(Space.WORLD, position).sub(this.cameraPosition);
    var cosi = I.dot(N);
    var eta = Math.max(1 - blend, 0.00001);
    var c = Math.abs(cosi);
    var g = eta * eta - 1 + c * c;
    if (g > 0) {
        g = Math.sqrt(g);
        var A = (g - c) / (g + c);
        var B = (c * (g + c) - 1) / (c * (g - c) + 1);
        return 0.5 * A * A * (1 + B * B);
    } else
        return 1;
}
function vronoiNoise(texCoords, scale) {
    var s = 2;
    var tmpMinX = 0;
    var tmpMaxX = 0;
    var tmpMinY = 0;
    var tmpMaxY = 0;
    while (s <= scale) {
        if (texCoords.x() < tmpMinX + 1 / s) {
            tmpMaxX = tmpMinX + 1 / s;
        } else {
            tmpMinX = tmpMinX + 1 / s;
            tmpMaxX = tmpMinX + 1 / s;
        }
        if (texCoords.y() < tmpMinY + 1 / s) {
            tmpMaxY = tmpMinY + 1 / s;
        } else {
            tmpMinY = tmpMinY + 1 / s;
            tmpMaxY = tmpMinY + 1 / s;
        }
        s *= 2;
    }
    var distance = calcDistance(tmpMinX, tmpMinY, scale, texCoords);
    return distance;
}
function calcDistance(MinX, MinY, scale, texCoords) {
    var nMinX = MinX - 1 / scale, nMinY = MinY - 1 / scale;
    var firstClosest = Distance(nMinX + 1 / scale, nMinX + 2 / scale, nMinY, nMinY + 1 / scale, texCoords);
    var secondClosest = Distance(nMinX + 1 / scale, nMinX + 2 / scale, nMinY, nMinY + 1 / scale, texCoords);
    for (var j = 1; j < 32; j++)
        for (var i = 1; i < 32; i++) {
            var minX = nMinX + (i - 1) / scale;
            var maxX = nMinX + i / scale;
            var minY = nMinY + (j - 1) / scale;
            var maxY = nMinY + j / scale;
            var tmp = Distance(minX, maxX, minY, maxY, texCoords);
            if (tmp < firstClosest) {
                secondClosest = firstClosest;
                firstClosest = tmp;
            } else if (tmp < secondClosest)
                secondClosest = tmp;
        }
    return secondClosest + firstClosest;
}
function Distance(minX, maxX, minY, maxY, texCoords) {
    var e = 3;
    if (minX < 0 || minY < 0 || maxX > 1 || maxY > 1)
        return 100;
    var point = randomPointGenerator(minX, maxX, minY, maxY).sub(texCoords);
    return point.dot(point);
}
function randomPointGenerator(minX, maxX, minY, maxY) {
    var seed = new Vec2(minX * _env.scale, minY * _env.scale);
    var rand = snoise(seed);
    return new Vec2(rand * (maxX - minX) + minX, rand * (maxY - minY) + minY);
}
function mod289(x) {
    return x.sub(Math.floor(x.mul(1 / 289)).mul(289));
}
function permute(x) {
    return mod289(x.mul(34).add(1).mul(x));
}
function snoise(v) {
    var C = new Vec4((3 - Math.sqrt(3)) / 6, 0.5 * (Math.sqrt(3) - 1), -1 + 2 * (3 - Math.sqrt(3)) / 6, 1 / 41);
    var i = Math.floor(v.add(v.dot(C.yy())));
    var x0 = v.sub(i).add(i.dot(C.xx()));
    var i1;
    i1 = x0.x > x0.y ? new Vec2(1, 0) : new Vec2(0, 1);
    var x12 = x0.xyxy().add(C.xxzz());
    x12.xy -= i1;
    i = mod289(i);
    var p = permute(permute(new Vec3(0, i1.y(), 1).add(i.y())).add(i.x()).add(new Vec3(0, i1.x(), 1)));
    var tmp = new Vec3(0.5).sub(x0.dot(x0), x12.xy().dot(x12.xy()), x12.zw().dot(x12.zw()));
    var m = Math.max(tmp, 0);
    m = m.mul(m);
    m = m.mul(m);
    var x = Math.fract(p.mul(C.www())).mul(2).sub(1);
    var h = Math.abs(x).sub(0.5);
    var ox = Math.floor(x.add(0.5));
    var a0 = x.sub(ox);
    m = m.mul(a0.mul(a0).add(h.mul(h)).mul(-0.85373472095314).add(1.79284291400159));
    var g = new Vec3(a0.x() * x0.x() + h.x() * x0.y(), a0.yz().mul(x12.xz()).add(h.yz().mul(x12.yw())));
    return 130 * m.dot(g);
}