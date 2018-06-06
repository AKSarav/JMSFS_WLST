package com.cscglobal.sre.SonicMQ.SonicStatsMonitor;

import com.cscglobal.sre.SonicMQ.SonicStatsMonitor.BrokerConnectionDetails;
import com.cscglobal.sre.SonicMQ.SonicStatsMonitor.Common;
import com.sonicsw.mq.common.runtime.IDurableSubscriptionData;
import com.sonicsw.mq.common.runtime.IQueueData;
import com.sonicsw.mq.mgmtapi.runtime.IBrokerProxy;
import com.sonicsw.mq.mgmtapi.runtime.MQProxyFactory;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.concurrent.TimeUnit;
import javax.management.ObjectName;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class CollectBrokerStats {

   private static Logger logger = LogManager.getLogger(CollectBrokerStats.class);


   public static void main(String[] args) {
      SimpleDateFormat dfStart = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a");
      logger.info("CollectBrokerStats Utility Starting at " + dfStart.format(new Date()));
      BrokerConnectionDetails bcd = Common.getBrokerConnection();
      IBrokerProxy broker = null;

      try {
         ObjectName t = new ObjectName(bcd.getJmxBeanName());
         broker = MQProxyFactory.createBrokerProxy(bcd.getJcc(), t);
      } catch (Exception var22) {
         logger.fatal("COLLECTBROKERSTATS IS UNABLE TO OBTAIN A BROKER PROXY - EXITING!!");
         logger.fatal("Stack Trace:", var22);
         System.exit(1);
      }

      logger.debug("Connected and Broker Proxy obtained...");

      try {
         logger.debug(" Retrieving Users with Durable Subscriptions");
         ArrayList t1 = broker.getUsersWithDurableSubscriptions((String)null);
         logger.debug(t1.size() + " Users with Durable Subscriptions found");
         Iterator qItem = t1.iterator();

         while(qItem.hasNext()) {
            String qlist = (String)qItem.next();
            ArrayList subscrList = broker.getDurableSubscriptions(qlist);
            logger.debug(subscrList.size() + " Subscriptions retrieved for User " + qlist);
            logger.debug("\nThere are " + subscrList.size() + " durable subscriptions for User: " + qlist);
            Iterator var9 = subscrList.iterator();

            while(var9.hasNext()) {
               IDurableSubscriptionData subdata = (IDurableSubscriptionData)var9.next();
               if(!subdata.getUser().equals("Administrator") || !subdata.getTopicName().contains("SonicMQ.")) {
                  boolean daysSinceLastConnect = false;
                  String dateStr = null;
                  int daysSinceLastConnect1;
                  if(subdata.getLastConnectedTime() == -1L) {
                     dateStr = "ACTIVE";
                     daysSinceLastConnect1 = 0;
                  } else {
                     Date theDate = new Date(subdata.getLastConnectedTime());
                     SimpleDateFormat dfSub = new SimpleDateFormat("yyyy-MM-dd hh:mm a");
                     dateStr = dfSub.format(theDate);
                     Date now = new Date();
                     long diff = now.getTime() - theDate.getTime();
                     daysSinceLastConnect1 = (int)TimeUnit.DAYS.convert(diff, TimeUnit.MILLISECONDS);
                  }

                  logger.info("\tUserID = " + subdata.getUser() + " Topic = " + subdata.getTopicName() + " SubscriptionName = " + subdata.getSubscriptionName() + " ClientID = " + subdata.getClientID() + " SubscriptionMessageCount = " + subdata.getMessageCount() + " TotalSubscriptionSize = " + subdata.getMessageSize() + " LastConnectedAt = " + dateStr + " DaysSinceLastConnect = " + daysSinceLastConnect1);
System.out.println("<tr><td>UserID</td><td>" + subdata.getUser() + "</td></tr> <tr><td>Topic</td><td>" + subdata.getTopicName() + "</td></tr> <tr><td>SubscriptionName</td><td>" + subdata.getSubscriptionName() + "</td></tr> <tr><td>ClientID</td><td>" + subdata.getClientID() + "</td></tr> <tr><td>TotalSubscriptionSize</td><td>" + subdata.getMessageSize() + "</td></tr> <tr><td>LastConnectedAt</td><td>" + dateStr + "</td></tr> <tr><td>DaysSinceLastConnect</td><td>" + daysSinceLastConnect1 + "</td></tr>");
               }
            }
         }

         logger.debug("Querying queues");
         ArrayList qlist1 = broker.getQueues((String)null);
         Iterator subscrList1 = qlist1.iterator();

         while(subscrList1.hasNext()) {
            IQueueData qItem1 = (IQueueData)subscrList1.next();
            logger.info("QueueName = " + qItem1.getQueueName() + " QueueMessageCount = " + qItem1.getMessageCount() + " QueueSize = " + qItem1.getTotalMessageSize());
         }
      } catch (Throwable var23) {
         logger.fatal("FATAL ERROR DURING EXECUTION - STACK TRACE FOLLOWS - EXITING!");
         logger.fatal("Stack Trace:", var23);
      } finally {
         if(bcd.getJcc() != null) {
            bcd.getJcc().disconnect();
         }

         SimpleDateFormat dfEnd = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss a");
         logger.info("CollectBrokerStats Utility Ending at " + dfEnd.format(new Date()));
      }

   }
}
