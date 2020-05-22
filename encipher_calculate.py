from PIL import Image
import random
import bcrypt
import hashlib
import math

def creatKey(imageName):

    image = Image.open(imageName)
    image_m = image.size[0]
    image_n = image.size[1]

    # 生成s_r
    s_r = ''
    for i in range(0, 64):
        s_r += chr(random.randint(33, 127))

    # s_M
    s_M = ''
    for i in range(0, 32):
        randomm = random.randint(0, image_m - 1)
        randomn = random.randint(0, image_n - 1)
        randomg = random.randint(0, 2)
        s_M += str(hex(image.getpixel((randomm, randomn))[randomg]))[2:4]

    # bcrypt
    bcrypt_salt = '$2b$10$' + s_M[0:32]
    bcrypt_res = bcrypt.hashpw(s_r.encode('utf-8'), bcrypt_salt.encode('utf-8'))

    # SHA512
    sha_512 = hashlib.sha512()
    sha_512.update(bcrypt_res + s_M[32:64].encode('utf-8'))
    return sha_512.hexdigest()

def encrypt_diff(imageName, key, Mp):

    image = Image.open(imageName)
    image_m = image.size[0]
    image_n = image.size[1]
    Mp_size = sum(map(sum,Mp))

    # 初值计算
    mu_1 = 3.9 + (int(key[0:12], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_2 = 3.9 + (int(key[12:24], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_3 = 3.9 + (int(key[24:36], 16) % 0x5AF3107A3FFF) / 1000000000000000

    x0_1 = (int(key[36:50], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_2 = (int(key[50:64], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_3 = (int(key[64:78], 16) % 0x2386F26FC0FFFF) / 10000000000000000

    begin_1 = int(key[78:82], 16)
    begin_2 = int(key[82:86], 16)
    begin_3 = int(key[86:90], 16)

    # Logisic映射得到扩散序列
    L_1 = [0] * (Mp_size + 2)
    L_2 = [0] * (Mp_size + 2)
    L_3 = [0] * (Mp_size + 2)
    # (1)
    x = x0_1
    mu = mu_1
    mark_i = 1                                                          # 记录序列长度
    for i in range(0, 10000 + begin_1):                                 # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_1[mark_i-1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1
    # (2)
    x = x0_2
    mu = mu_2
    mark_i = 1
    for i in range(0, 10000 + begin_2):                                 # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_2[mark_i-1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1
    # (3)
    x = x0_3
    mu = mu_3
    mark_i = 1
    for i in range(0, 10000 + begin_3):                                 # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_3[mark_i-1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1

    # 图像加密处理
    mark_i = 1
    for i in range(0, image_m):
        for j in range(0, image_n):
            if Mp[i][j] == 0:
                continue
            numberOf3 = mark_i % 3
            if numberOf3 == 1:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_1[mark_i - 1],
                    image.getpixel((i, j))[1] ^ L_2[mark_i - 1],
                    image.getpixel((i, j))[2] ^ L_3[mark_i - 1]))
            if numberOf3 == 2:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_3[mark_i],
                    image.getpixel((i, j))[1] ^ L_1[mark_i],
                    image.getpixel((i, j))[2] ^ L_2[mark_i]))
            if numberOf3 == 0:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_2[mark_i + 1],
                    image.getpixel((i, j))[1] ^ L_3[mark_i + 1],
                    image.getpixel((i, j))[2] ^ L_1[mark_i + 1]))
            mark_i += 1
    return image


def encrypt_rep(imageAfterDiff, key, Mp):

    image = imageAfterDiff
    image_m = image.size[0]
    image_n = image.size[1]
    Mp_size = sum(map(sum,Mp))

    # 初值计算
    mu_1 = 3.9 + (int(key[68:80], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_2 = 3.9 + (int(key[80:92], 16) % 0x5AF3107A3FFF) / 1000000000000000

    x0_1 = (int(key[92:106], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_2 = (int(key[106:120], 16) % 0x2386F26FC0FFFF) / 10000000000000000

    begin_1 = int(key[120:124], 16)
    begin_2 = int(key[124:128], 16)

    # Logisic映射得到扩散序列
    L_1 = [0] * Mp_size
    L_2 = [0] * Mp_size
    mark_i = 1                                                          # 记录序列长度
    for i in range(0, 10000 + begin_1):                                 # 预迭代
        x0_1 = mu_1 * x0_1 - mu_1 * x0_1 * x0_1
    for i in range(0, 10000 + begin_2):                                 # 预迭代
        x0_2 = mu_2 * x0_2 - mu_2 * x0_2 * x0_2
    while (1):
        x0_1 = mu_1 * x0_1 - mu_1 * x0_1 * x0_1
        x0_2 = mu_2 * x0_2 - mu_2 * x0_2 * x0_2
        if 0.3 <= x0_1 and x0_1 < 0.7 and 0.3 <= x0_2 and x0_2 < 0.7 :
            num1 = math.floor(2.5 * image_m * x0_1 - 0.75 * image_m + 1)
            num2 = math.floor(2.5 * image_n * x0_2 - 0.75 * image_n + 1)
            if Mp[num1 - 1][num2 - 1] == 1:
                L_1[mark_i - 1] = num1
                L_2[mark_i - 1] = num2
                if mark_i == Mp_size:
                    break
                mark_i += 1
    mark_i = 1
    for i in range(0, image_m):
        for j in range(0, image_n):
            if Mp[i][j] == 1:
                temp = image.getpixel((i, j))
                image.putpixel(
                    (i, j),
                    image.getpixel((L_1[mark_i - 1] - 1, L_2[mark_i - 1] - 1))
                )
                image.putpixel(
                    (L_1[mark_i - 1] - 1, L_2[mark_i - 1] - 1),
                    temp
                )
                mark_i += 1
    return image

# 解密-扩散
def decrypt_diff(imageAfterDeRep, key, Mp):

    image = imageAfterDeRep
    image_m = image.size[0]
    image_n = image.size[1]
    Mp_size = sum(map(sum, Mp))

    # 初值计算
    mu_1 = 3.9 + (int(key[0:12], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_2 = 3.9 + (int(key[12:24], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_3 = 3.9 + (int(key[24:36], 16) % 0x5AF3107A3FFF) / 1000000000000000

    x0_1 = (int(key[36:50], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_2 = (int(key[50:64], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_3 = (int(key[64:78], 16) % 0x2386F26FC0FFFF) / 10000000000000000

    begin_1 = int(key[78:82], 16)
    begin_2 = int(key[82:86], 16)
    begin_3 = int(key[86:90], 16)

    # Logisic映射得到扩散序列
    L_1 = [0] * (Mp_size + 2)
    L_2 = [0] * (Mp_size + 2)
    L_3 = [0] * (Mp_size + 2)
    # (1)
    x = x0_1
    mu = mu_1
    mark_i = 1  # 记录序列长度
    for i in range(0, 10000 + begin_1):  # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_1[mark_i - 1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1
    # (2)
    x = x0_2
    mu = mu_2
    mark_i = 1
    for i in range(0, 10000 + begin_2):  # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_2[mark_i - 1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1
    # (3)
    x = x0_3
    mu = mu_3
    mark_i = 1
    for i in range(0, 10000 + begin_3):  # 预迭代
        x = mu * x - mu * x * x
    while (1):
        x = mu * x - mu * x * x
        if 0.3 <= x and x < 0.7:
            L_3[mark_i - 1] = math.floor(640 * (x - 0.3))
            if mark_i == Mp_size + 2:
                break
            mark_i += 1

    # 图像加密处理
    mark_i = 1
    for i in range(0, image_m):
        for j in range(0, image_n):
            if Mp[i][j] == 0:
                continue
            numberOf3 = mark_i % 3
            if numberOf3 == 1:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_1[mark_i - 1],
                    image.getpixel((i, j))[1] ^ L_2[mark_i - 1],
                    image.getpixel((i, j))[2] ^ L_3[mark_i - 1]))
            if numberOf3 == 2:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_3[mark_i],
                    image.getpixel((i, j))[1] ^ L_1[mark_i],
                    image.getpixel((i, j))[2] ^ L_2[mark_i]))
            if numberOf3 == 0:
                image.putpixel((i, j), (
                    image.getpixel((i, j))[0] ^ L_2[mark_i + 1],
                    image.getpixel((i, j))[1] ^ L_3[mark_i + 1],
                    image.getpixel((i, j))[2] ^ L_1[mark_i + 1]))
            mark_i += 1
    return image

# 解密-置换
def decrypt_rep(imageName, key, Mp):

    image = Image.open(imageName)
    image_m = image.size[0]
    image_n = image.size[1]
    Mp_size = sum(map(sum,Mp))

    # 初值计算
    mu_1 = 3.9 + (int(key[68:80], 16) % 0x5AF3107A3FFF) / 1000000000000000
    mu_2 = 3.9 + (int(key[80:92], 16) % 0x5AF3107A3FFF) / 1000000000000000

    x0_1 = (int(key[92:106], 16) % 0x2386F26FC0FFFF) / 10000000000000000
    x0_2 = (int(key[106:120], 16) % 0x2386F26FC0FFFF) / 10000000000000000

    begin_1 = int(key[120:124], 16)
    begin_2 = int(key[124:128], 16)

    # Logisic映射得到扩散序列
    L_1 = [0] * Mp_size
    L_2 = [0] * Mp_size
    mark_i = 1                                                          # 记录序列长度
    for i in range(0, 10000 + begin_1):                                 # 预迭代
        x0_1 = mu_1 * x0_1 - mu_1 * x0_1 * x0_1
    for i in range(0, 10000 + begin_2):                                 # 预迭代
        x0_2 = mu_2 * x0_2 - mu_2 * x0_2 * x0_2
    while (1):
        x0_1 = mu_1 * x0_1 - mu_1 * x0_1 * x0_1
        x0_2 = mu_2 * x0_2 - mu_2 * x0_2 * x0_2
        if 0.3 <= x0_1 and x0_1 < 0.7 and 0.3 <= x0_2 and x0_2 < 0.7 :
            num1 = math.floor(2.5 * image_m * x0_1 - 0.75 * image_m + 1)
            num2 = math.floor(2.5 * image_n * x0_2 - 0.75 * image_n + 1)
            if Mp[num1 - 1][num2 - 1] == 1:
                L_1[mark_i - 1] = num1
                L_2[mark_i - 1] = num2
                if mark_i == Mp_size:
                    break
                mark_i += 1
    mark_i = Mp_size
    for i in range(image_m - 1, -1, -1):
        for j in range(image_n - 1, -1, -1):
            if Mp[i][j] == 1:
                temp = image.getpixel((i, j))
                image.putpixel(
                    (i, j),
                    image.getpixel((L_1[mark_i - 1] - 1, L_2[mark_i - 1] - 1))
                )
                image.putpixel(
                    (L_1[mark_i - 1] - 1, L_2[mark_i - 1] - 1),
                    temp
                )
                mark_i -= 1
    return image