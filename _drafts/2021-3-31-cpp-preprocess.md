---
layout: post
title: C/C++ 宏编程解析
categories: c++
catalog: true
tags: [dev]
description: |
    todo
figures: []
---
{% include asset_path %}

本文的目前是要讲清楚 C/C++ 的宏编程的规则和实现方法，让你不再惧怕看到代码里面的宏。我会首先说说 C++ 标准 14 里面提到的关于宏展开的规则，然后通过修改 Clang 的源码来观察宏展开，最后基于这些知识来聊聊宏编程的实现。

## 引子

我们可以通过执行命令 `gcc -P -E a.cpp -o a.cpp.i` 来让编译器对文件 `a.cpp` 只执行预处理并保存结果到 `a.cpp.i` 中。

首先我们先来看一些例子:

#### 递归

``` cpp
#define ITER(arg1, arg2) ITER(arg2, arg1) 

ITER(1, 2)
```

宏 `ITER` 交换了 `arg1`, `arg2` 的位置。宏展开之后，得到的是：

``` cpp
ITER(2, 1)
```

可以看到，`arg1` `arg2` 的位置成功交换，在这里宏成功展开了一次，也只展开了一次，不再递归。换言之，宏的展开过程中，是不可自身递归，如果在递归的过程中发现相同的宏在之前的递归中已经展开过，则不再展开，这是宏展开的其中一条重要的规则。禁止递归的原因也很简单，就是为了避免无限递归。

#### 字符串连接

``` cpp
#define CONCAT(arg1, arg2) arg1 ## arg2

CONCAT(Hello, World)

CONCAT(Hello, CONCAT(World, !))
```

宏 `CONCAT` 目的是连接 `arg1` `arg2`。宏展开之后，得到的是：

``` cpp
HelloWorld

HelloCONCAT(World, !)
```

`CONCAT(Hello, World)` 能够得到正确的结果 `HelloWorld`。但是 `CONCAT(Hello, CONCAT(World, !))` 却只展开了外层的宏，内层的 `CONCAT(World, !)` 并没有展开而是直接跟 `Hello` 连接在了一起了，这跟我们预想的不一样，我们真正想要的结果是 `HelloWorld!`。这就是宏展开的另外一条重要的规则：跟在 `##` 宏连接符后面的宏参数，不会执行展开，而是会直接跟前面的内容先连接在一起。

通过上面两个例子可以看出来，宏展开的规则有一些是反直觉的，如果不清楚具体的规则，有可能写出来的宏跟我们想要的效果不一致。

## 宏展开规则

通过引子的两个例子，我们了解到了宏展开是有一套标准的规则的，这套规则定义在 C/C++ 标准里面，内容不多，建议先仔细读几遍，我这里顺带给下标准 n4296 版本的链接，宏展开在 16.3 节：[传送门](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4296.pdf)。下面我挑出 n4296 版本中几条重要的规则，这些规则会决定如何正确编写宏（还是建议抽时间把标准里面宏展开细读下）。

### 宏参数展开

在对宏进行展开的时候，如果宏的参数也是可以展开的宏，会先把参数完全展开，再展开宏，例如

``` cpp
#define ADD_COMMA(arg1, arg2) arg1, arg2

ADD_COMMA(ADD_COMMA(1, 2), ADD_COMMA(3, 4))     // 1, 2, 3, 4
```

一般情况下的宏展开，都可以认为是先对参数求值，再对宏求值，但是有一些例外的情况需要注意（ `#` 和 `##` 操作符）。

### `#` 操作符

`#` 操作符后面跟的宏参数，不会进行展开，会直接字符串化，例如：

``` cpp
#define STRINGIZE(arg1) # arg1

STRINGIZE(a)                // "a"

STRINGIZE(STRINGIZE(a))     // "STRINGIZE(a)"
```

根据这条规则 `STRINGIZE(STRINGIZE(a))` 只能展开为 `"STRINGIZE(a)"`。

### `##` 操作符

`##` 操作符前后的宏参数，都不会进行展开，会先直接连接起来，例如：

``` cpp
#define CONCAT(arg1, arg2) arg1 ## arg2

CONCAT(Hello, World)                // HelloWorld

CONCAT(Hello, CONCAT(World, !))     // HelloCONCAT(World, !)

CONCAT(CONCAT(Hello, World) C, ONCAT(!)     // CONCAT(Hello, World) CONCAT(!)
```

### 重复展开

预处理器通过分析文本，识别出待展开的宏以及该宏的参数，然后对该宏执行重复展开：执行完一次宏展开之后，会重新扫描得到的内容，继续展开，直到没有可以展开的内容为止。

一次宏展开，可以理解为把该宏的参数完全展开（注意 `#` 和 `##` 的特殊处理），之后根据宏的定义，把宏和完全展开后的参数替换成定义的形式，再处理定义中的所有 `#` 和 `##` 操作符。

``` cpp
#define CONCAT(arg1, arg2) arg1 ## arg2
#define STRINGIZE(arg1) # arg1

CONCAT(CON, CAT(Hello, World))    // CONCAT(Hello, World)

CONCAT(STRING, IZE(Hello))        // -> STRINGIZE(Hello) -> "Hello"
```

`CONCAT(CON, CAT(Hello, World))` 第一次扫描展开得到了 `CONCAT(Hello, World)`，看上去还是宏，但由于 `CONCAT` 已经展开过了不会再递归展开，所以就停止了。

`CONCAT(STRING, IZE(Hello))` 第一次扫描展开得到 `STRINGIZE(Hello)`，然后执行第二次扫描，发现可以继续展开，最后得到 `"Hello"`。

### 禁止递归

在重复展开的过程中，禁止递归展开相同的宏。可以把宏展开理解为树形的结构，根节点就是一开始要展开的宏，每

可以把展开宏理解为函数调用，重复展开就是：如果函数调用得到的结果还是包含函数，则继续执行函数调用。但是，如果得到的函数，在之前已经调用过了，则禁止继续调用这个函数。

如果给每一次重复扫描展开进行编号，那么第 N 次的扫描展开中，不会再展开前面 0...N-1 次展开中展开过的宏，例如：

CONCAT(CONCAT(C, O), NCAT_1(a, b))

CONCAT(C, ONCAT(a, b))

CONCAT(C, CONCAT(C, ONCAT(a, b)))