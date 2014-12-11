#SMS日志命令

每条记录都以'# '开头，代码中省略。

##节点状态

###queued

###submitted

###active

###complete

###aborted


#变量

###alter

###meter

正常记录（LOG）

出错时的记录（ERR）
	
	ERR:[03:41:58 10.7.2014] meter:WaitingMins for /grapes_meso_v4_0/cold/00/pre_data/obs_get/aob_get:the node was not found:
	ERR:[12:52:00 19.5.2014] meter:/gmf_gsi_v1r5/T639/06/dasrefresh:WaitingMins: 55 out of range [0 - 40]


###set

设置事件
	
	LOG:[23:49:24 10.11.2014] set:/gmf_gsi_v1r5/T639/18/obs/sst_make:sstready
 
###event	

一般在出错的时候才有

	ERR:[00:23:36 1.10.2014] event:actived for /gmf_gsi_v1r5/T639/18/model/mod_gf:the node was not found:

等等 

##节点干预操作

###force

强制设置节点状态，包括使用kill命令杀掉任务

	MSG:[00:36:05 7.10.2014] force:/grapes_meso_v4_0/cold/12/model/fcst to queued by nwp@10848782
	MSG:[21:24:37 21.9.2014] force:/extend_v2_1/subsys/uvi/12/uvi to complete by nwp@10493355
	MSG:[03:21:18 13.9.2014] force:/obs_reg/aob/00E/obs_get/getobs_rgwst to aborted by nwp@10266057
 
###delete

删除依赖关系，用于补做

	MSG:[04:17:51 7.10.2014] delete:/gmf_gsi_v1r5/T639/00 time by nwp@10655492

###requeue

重新排队，用于补做

	 MSG:[23:55:16 6.10.2014] requeue:user nwp@10651712:/gda_gsi_v1r5/T639/12/an/gsi

###run

重新运行，界面中的excute

	 LOG:[03:08:02 18.6.2014] run:/gda_ssi_v1/T213/18/an/ssi by nwp@7797433

###cancel

取消节点，用于重新部署任务
	
	LOG:[10:27:11 31.3.2014] cancel:/gmf_gsi_v1r5/T639/00/prods/grib2/grads2grib2_000/alias0 by nwp@5801977
	LOG:[02:56:54 9.4.2014] cancel:/gda_gsi_v1r5 by nwp@6018242
 
##非常用命令

###autorepeat date

更新时间，后面接begin

	 MSG:[03:31:30 19.9.2014] autorepeat date:/gda_gsi_v1r5 started

###begin

紧随autorepeat date，任务开始

	MSG:[02:32:29 29.6.2014] begin:/grapes_meso_3_3 started automatically
 
###abort
	
自动重做时记录的日志，与aborted一同出现

	WAR:[00:45:17 7.10.2014] abort:/gmf_gsi_v1r5/T639/18/dasrefresh ---> try number 1

##系统命令

###checkpoint

运行状态存盘

	LOG:[03:31:30 19.9.2014] checkpoint:written into cma20n03.check by SMS

###login

	MSG:[00:23:35 1.10.2014] login:User nwp@10719460 with password from cma20n03

###logout

	MSG:[00:23:35 1.10.2014] logout:User nwp@10719460

###timeout

	WAR:[00:03:04 9.11.2014] timeout:user nwp@11617341 timed out

###zombie
	
	WAR:[11:54:40 19.5.2014] zombie:created new network zombie /gda_ssi_v1/T213/00/obs/tcreport_get from cma18n04 sender cma20n03

##内部日志

### 进程

####非结构化PID

进程出错，后面紧跟aborted
	
	ERR:[03:40:31 8.7.2014] PID 14352534 exited with status 127 [llsubmit2 /cma/g1/nwp/SMSOUT/gmf_ssi_v1/T213/00/obs/atovs_get.job2 /gmf_ssi_v1/T213/00/obs/atovs_get]


####SMS-PROCESS-SYS

####SMS-PROCESS-CHILD

###认证

####SMS-PROG-1

	ERR:[00:44:01 8.4.2014] SMS-PROG-1:User 1050695,10506 from cma18n01 not registered

##其它

###check

	MSG:[09:01:04 4.4.2014] check:method time interval 120 sec by nwp@5901621

###dir

###clear
 
取消事件

	LOG:[03:14:01 21.9.2014] clear:/gda_ssi_v1/T213/12/obs/tcreport_get:arrived
