// pages/book/book.js
Page({

  /**
   * 页面的初始数据
   */
  data: {



    sexItem:[
    {value:"man",name:"男"},
    {value:"woman",name:"女"}
    ],
    teacherItem:[
      {value:"ymx",name:"应梦娴"},
      {value:"lxf",name:"梁羡飞"},
      {value:"ln",name:"李娜"},
      {value:"tw",name:"田薇"}
    ],
    dateItem:[
      {value:"date1",name:"2021年3月8日 周一",numbers:"5",disabled:false},
      {value:"date2",name:"2021年3月9日 周二",numbers:"5",disabled:false},
      {value:"date3",name:"2021年3月10日 周三",numbers:"5",disabled:false},
      {value:"date4",name:"2021年3月11日 周四",numbers:"5",disabled:false},
      {value:"date5",name:"2021年3月12日 周五",numbers:"5",disabled:false}
    ],
    timeItem:[
      {value:"time1",name:"09:00-09:50",numbers:"1",disabled:false},
      {value:"time2",name:"10:00-10:50",numbers:"0",disabled:true},
      {value:"time3",name:"14:00-14:50",numbers:"0",disabled:true},
      {value:"time4",name:"15:00-15:50",numbers:"1",disabled:false},
      {value:"time5",name:"16:00-16:50",numbers:"1",disabled:false}
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
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
    console.log(this)
    console.log(e.detail.value)
    console.log(this.__data__.list.schedule[e.detail.value])
    this.setData(
      {
        hoursItem:this.__data__.list.schedule[e.detail.value],
      }
    )
    console.log(e)
  }

})