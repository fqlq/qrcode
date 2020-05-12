# QR-code

Forked from [sylnsfar/qrcode](https://github.com/sylnsfar/qrcode)

### Differences from the original library

1. This project allows you to create colorized qrcodes
2. Qrcode scaling algorithm has been completely rewritten - result image will be sharp with any scaling factor
3. This project includes Flask server with simple API

### JSON API request example

```
{
  text: 'Hello, world',
  scale: 10,
  version: 6.
  type: 'covered',
	version: 6,
	image: <IMAGE-URL>,
	color: #ff0000
}
```

### Examples

![](https://habrastorage.org/webt/sl/zx/kq/slzxkqbopffvgzw1mryarbhz7rk.png)

![](https://habrastorage.org/webt/pd/oy/fj/pdoyfjdpsctc5q9rifnyz63sngi.png)

![](https://habrastorage.org/webt/fq/a4/0a/fqa40a2zgpk9p25xveuu5vwhbvk.png)

### Usage

This project is ready for deploy on [Heroku](https://www.heroku.com/) - read more [here](https://devcenter.heroku.com/articles/github-integration)
