Page({
    data: {
        showTopTips: false,

        sex: ["男", "女"],
        sexIndex: -1,

        dateIndex: -1,
        hourIndex: -1,
        hourIndex: -1,
        teacherIndex: -1,
        list: {

        },
        length: 0,
        formData: {},
        rules: [{
                name: 'name',
                rules: {
                    required: true,
                    message: '请输入姓名'
                },
            },
            {
                name: 'sex',
                rules: {
                    required: true,
                    message: '请选择性别'
                },
            },
            {
                name: 'studentid',
                rules: {
                    required: true,
                    message: '学号为必填项'
                },
            },
            {
                name: 'tel',
                rules: [{
                    required: true,
                    message: '手机号码为必填项'
                }, {
                    mobile: true,
                    message: '手机号码格式不正确'
                }],
            },
            {
                name: 'teacher',
                rules: [{
                    required: true,
                    message: '请选择一名辅导员'
                }],
            },
            {
                name: 'date',
                rules: [{
                    required: true,
                    message: '请选择日期'
                }],
            },
            {
                name: 'hour',
                rules: [{
                    required: true,
                    message: '请选择时间'
                }],
            },
            {
                name: 'difficulties',
                rules: [{
                    required: true,
                    minlength: 10,
                    maxlength: 200,
                    message: '困惑与希望得到的帮助请多于10字且少于140字'
                }],
            },

        ]
    },

    onLoad: function (options) {
        var that = this
        wx.request({
            url: 'https://www.bugstop.site/available/',
            headers: {
                'Content-Type': 'application/json'
            },
            success(res) {
                //将获取到的json数据，存在名字叫list的这个数组中

                that.setData({
                    list: res.data,
                    //res代表success函数的事件对，data是固定的，list是数组
                })

            }
        })

    },

    textareaInput: function (e) {
        console.log(e)
        this.setData({
            length: e.detail.value.length,
            [`formData.difficulties`]: e.detail.value

        })
    },

    bindTeacherChange: function (e) {
        var list = this.data.list;
        this.setData({
            teacherIndex: e.detail.value,
            [`formData.teacher`]: list.teachers[e.detail.value]
        })
    },

    bindDateChange: function (e) {
        var list = this.data.list;
        this.setData({
            dateIndex: e.detail.value,
            [`formData.date`]: list.date[e.detail.value]
        })
    },

    formInputChange(e) {
        const {
            field
        } = e.currentTarget.dataset
        this.setData({
            [`formData.${field}`]: e.detail.value
        })
    },

    bindHourChange: function (e) {
        var list = this.data.list;

        this.setData({
            hourIndex: e.detail.value,
            [`formData.hour`]: list.hour[e.detail.value]

        })
    },
    bindSexChange: function (e) {
        var sex = this.data.sex
        this.setData({
            sexIndex: e.detail.value,
            [`formData.sex`]: sex[e.detail.value]
        })

    },


    submitForm() {
        var formdata=this.data.formData;
        this.selectComponent('#form').validate((valid, errors) => {
            console.log('valid', valid, errors)
            if (!valid) {
                const firstError = Object.keys(errors)
                if (firstError.length) {
                    this.setData({
                        error: errors[firstError[0]].message
                    })

                }
            } else {
                wx.showLoading({
                    title: "提交中",
                    mask: true
                });
                console.log(formdata);
                wx.request({
                    url: 'https://www.bugstop.site/reserve/',
                    data: formData,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000,
                    method: "POST",
                    success(res) {
                        console.log(res.data)
                        wx.hideLoading()
                        switch (res.data.statusCode) {
                            case 500:
                                wx.showToast({
                                    title: "预约成功！",
                                    icon: 'success', //如果要纯文本，不要icon，将值设为'none'
                                    mask: true,
                                    duration: 3000
                                })

                                setTimeout(function () {
                                    wx.reLaunch({
                                        url: '/pages/index/index'
                                    })
                                }, 2000)

                                break;

                        }
                    },
                    fail() {
                        wx.hideLoading()
                        wx.showToast({
                            title: "提交超时，请稍候重试",
                            icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                            mask: true
                        })
                    }

                })
            }
        })
        // this.selectComponent('#form').validateField('mobile', (valid, errors) => {
        //     console.log('valid', valid, errors)
        // })
    }
});