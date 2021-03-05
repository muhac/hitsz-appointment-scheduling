// pages/book/book.js
import WxValidate from "../../utils/validate";

Page({

  /**
   * 页面的初始数据
   */
  data: {



    sexItem:[
    {value:"m",name:"男"},
    {value:"f",name:"女"}
    ],

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.initValidate()
    var that = this
      wx.request({
        url: 'https://www.bugstop.site/available/',
        headers: {
          'Content-Type': 'application/json'
        },
        success (res) {
          //将获取到的json数据，存在名字叫list的这个数组中
          that.setData({
            list: res.data,
            //res代表success函数的事件对，data是固定的，list是数组
          })

        }
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },
  
  dateChange: function(e){
    this.setData(
      {
        hoursItem:this.__data__.list.schedule[e.detail.value],
        showhours:true
      }
    )
    console.log(e)
  },

  formSubmit(e) {
    let params = e.detail.value;
    if (!this.WxValidate.checkForm(params)) {
      //表单元素验证不通过，此处给出相应提示
        let error = this.WxValidate.errorList[0];
        wx.showToast({
          title: error.msg,
          icon: 'error',    //如果要纯文本，不要icon，将值设为'none'
          mask: true  
          })
          return false;
    }
    wx.showLoading(
      {
        title:"提交中",
        mask: true
      }
    );

    wx.request({
      url: 'https://www.bugstop.site/reserve/',
      data: params,
      headers: {
           'Content-Type': 'application/json'
      },
      timeout: "10000",
      method: "POST",
      success (res) {
        wx.hideLoading()
        switch(res.data.statusCode){
          case 500:
            wx.showToast({
              title: "预约成功！",
              icon: 'success',    //如果要纯文本，不要icon，将值设为'none'
              mask: true,
              duration: 3000
              })

              setTimeout(function(){
                wx.reLaunch({
                url: '/pages/index/index'
              })},2000)

              break;

        }
    },
    fail(){
      wx.hideLoading()
      wx.showToast({
        title: "提交超时，请稍候重试",
        icon: 'error',    //如果要纯文本，不要icon，将值设为'none'
        mask: true  
        })
    }
  
  })
},

  formReset: function () {
    console.log('form发生了reset事件')
  },

  initValidate() {
    let rules = {
      name: {
        required: true,
        maxlength: 10
      },
      sex: {
        required: true
      }
      ,
      grade: {
        required: true
      }, 
      studentid: {
        required: true,
        maxlength: 15
      },
      tel: {
        required: true,
        tel: true
      },
      teacher: {
        required: true
      },
      date: {
        required: true
      },
      time: {
        required: true
      },
      difficulties: {
        required: true,
        rangelength: [5,200]
      }
    }

    let message = {
      name: {
        required: '请输入姓名',
        maxlength: '名字不能超过10个字'
      },
      sex: {
        required: "请选择性别"
      },
      grade: {
        required: "请输入年级",
      },
      studentid: {
        required: "请输入学号",
        maxlength: "不能超过15个字符"
      },
      tel: {
        required: "请输入手机号码",
        tel: "请输入正确的手机号"
      },
      teacher: {
        required: "请选择辅导员"
      },
      date: {
        required: "请选择预约日期"
      },
      time: {
        required: "请选择预约时间"
      },
      difficulties: {
        required: "请简述目前遇到的困难和需要的帮助",
        rangelength: "请输入多于5字且少于200字的内容"
      }
    }
    //实例化当前的验证规则和提示消息
    this.WxValidate = new WxValidate(rules, message);
  }

})