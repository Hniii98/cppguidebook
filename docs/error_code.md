# 现代 C++ 错误处理知多少（未完工）

配套视频：[BV1QpWSekEJY](https://www.bilibili.com/video/BV1QpWSekEJY)

[TOC]

## 错误的分类

假设一个函数 `open` 的功能是打开文件。

```cpp
int open(const char *path) {
    if (!file_exists(path)) {
        // 如果找不到文件怎么办？
    }
    // 成功找到文件：
    return get_handle(path);
}

int main() {
    int file = open("file.txt");

    char buf[64];
    read(file, buf, sizeof buf);
    ...
}
```

理想情况下，所有的函数都能成功执行，都能正常返回结果……

可现实中，我们不能假设一个程序，永远正确执行（例如文件可能被用户误删除，或者内存不够用等）。

更有甚者，有时错误是计划的一部分（例如文件不存在，则创建一个新文件，而不是将其视为不可修复的错误）。

特别是涉及 IO 操作的任务，出现一些细小错误的情况是很多的。要区分哪些是可以修复的错误，哪些是不可挽回的错误。

例如当网络连接失败时，我们可以重新尝试连接两三次，如果还是不行，那才认为是真的失败了。

因此，我们把错误分为两大类：

- 可恢复错误：不是特别严重的，甚至是计划之中的，经常发生的错误。可以通过一定操作来弥补这类错误，或将其转化为其他不同类型的错误。
- 不可恢复错误：非常严重的错误，或者是发生概率很低平时没必要特殊处理的错误。一旦发生，整个程序都无法继续执行下去，必须全身而退，整个进程或线程都将终止。

### 不可恢复错误

不可恢复错误的处理最简单，我们只需要在被调用者检测到错误的分支中，直接调用 `exit` 函数“终止程序”即可。

```cpp
int open(const char *path) {
    if (!file_exists(path)) {
        // 找不到文件我就自杀！
        exit(1);
        // 程序不会执行到此
    }
    return get_handle(path);
}

int main() {
    int file = open("file.txt");

    char buf[64];
    read(file, buf, sizeof buf);
    ...
}
```

- 缺点：`exit` 会直接退出整个进程！没有任何给调用者挽回的机会，因此只能用于“不可恢复错误”这个类型。
- 优点：调用者无需做任何判断处理，写起来就好像被调用函数“总是成功”一样，总能返回结果。因为如果被调用者失败的话，他会调用 `exit` 自杀，就不会返回到调用者中了。

> {{ icon.fun }} 小时候看这集变成“码码的萤火虫”了。

### 可恢复错误

有时候，我们对于部分错误，是有挽回机会的，不希望因为一点可以修复的小错误就把整个程序终止掉。

要不要挽回应该由调用者的具体业务决定，而封装良好的 API（`open`）应该忠实地把错误报告给调用者（`main`）。

让调用者来决定要杀了还是抢救，而不是自作主张地直接自杀。

```cpp
int open(const char *path) {
    if (!file_exists(path)) {
        // 找不到文件，就返回 -1 这个“出错特殊值”代替
        return -1;
    }
    return get_handle(path);
}

int main() {
    int file = open("file.txt");
    if (file == -1) { // 缺点是 main 里面必须判断返回值是否为“出错特殊值”
        // 如果找不到文件，尝试进行处理
        create_empty_file("file.txt");
        // 重新尝试打开
        file = open("file.txt");
        if (file == -1) { // 如果还是出错，那就没救了
            exit(-1);     // 直接自杀
        }
    }

    char buf[64];
    read(file, buf, sizeof buf);
    ...
}
```

### 我该如何抉择

## 调用者与被调用者

`main` 是调用者，`open` 是被调用者。

被调用者函数可能产生错误，也可能正常执行。

## 提前返回是好习惯！

## 异常

## 错误码

## `std::error_code`

## `std::expected`

也可以 `boost::expected` 替代。
