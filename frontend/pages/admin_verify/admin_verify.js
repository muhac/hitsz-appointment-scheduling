Page({
  data: {
    Length: 6, //输入框个数
    isFocus: true, //聚焦
    Value: "", //输入的内容
    ispassword: true, //是否密文显示 true为密文， false为明文。
    disabled: true,
  },
  Focus(e) {
    var that = this;
    console.log(e.detail.value);
    var inputValue = e.detail.value;
    var ilen = inputValue.length;
    if (ilen == 6) {
      that.setData({
        disabled: false,
      })
    } else {
      that.setData({
        disabled: true,
      })
    }
    that.setData({
      Value: inputValue,
    })
  },
  Tap() {
    var that = this;
    that.setData({
      isFocus: true,
    })
  },
  formSubmit(e) {
    console.log(e.detail.value.password);
  },

  onLoad: function (options) {

  },
  onShow: function () {

  },
})