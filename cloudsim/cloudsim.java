
package org.cloudbus.cloudsim.examples;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.LinkedList;
import java.util.List;

import org.cloudbus.cloudsim.*;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.provisioners.*;

public class FCFS {

    private static List<Cloudlet> cloudletList;
    private static List<Vm> vmList;

    // Create Virtual Machines
    private static List<Vm> createVM(int userId, int vms) {
        LinkedList<Vm> list = new LinkedList<Vm>();

        int mips = 1000;
        long size = 10000;
        int ram = 512;
        long bw = 1000;
        int pesNumber = 1;
        String vmm = "Xen";

        for (int i = 0; i < vms; i++) {
            Vm vm = new Vm(i, userId, mips, pesNumber,
                    ram, bw, size, vmm,
                    new CloudletSchedulerSpaceShared());
            list.add(vm);
        }
        return list;
    }

    // Create Cloudlets
    private static List<Cloudlet> createCloudlet(
            int userId, int cloudlets) {

        LinkedList<Cloudlet> list = new LinkedList<Cloudlet>();

        long length = 4000;
        long fileSize = 300;
        long outputSize = 300;
        int pesNumber = 1;

        UtilizationModel utilization =
                new UtilizationModelFull();

        for (int i = 0; i < cloudlets; i++) {
            Cloudlet cloudlet = new Cloudlet(
                    i, length, pesNumber,
                    fileSize, outputSize,
                    utilization, utilization, utilization);

            cloudlet.setUserId(userId);
            cloudlet.setVmId(0);
            list.add(cloudlet);
        }
        return list;
    }

    public static void main(String[] args) {
        Log.printLine("Starting FCFS Resource Allocation...");

        try {
            // Initialize CloudSim
            CloudSim.init(1, Calendar.getInstance(), false);

            // Create Datacenter
            createDatacenter("Datacenter_0");

            // Create Broker
            DatacenterBroker broker =
                    new DatacenterBroker("Broker");
            int brokerId = broker.getId();

            // Create one VM and three Cloudlets
            vmList = createVM(brokerId, 1);
            cloudletList = createCloudlet(brokerId, 3);

            broker.submitVmList(vmList);
            broker.submitCloudletList(cloudletList);

            // Start simulation
            CloudSim.startSimulation();

            List<Cloudlet> result =
                    broker.getCloudletReceivedList();

            CloudSim.stopSimulation();

            // Display results
            printCloudletList(result);

            Log.printLine("FCFS Simulation Finished!");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Create Datacenter
    private static Datacenter createDatacenter(String name) {

        List<Host> hostList = new ArrayList<Host>();
        List<Pe> peList = new ArrayList<Pe>();

        peList.add(new Pe(0,
                new PeProvisionerSimple(1000)));

        int ram = 2048;
        long storage = 1000000;
        int bw = 10000;

        Host host = new Host(
                0,
                new RamProvisionerSimple(ram),
                new BwProvisionerSimple(bw),
                storage,
                peList,
                new VmSchedulerTimeShared(peList));

        hostList.add(host);

        DatacenterCharacteristics characteristics =
                new DatacenterCharacteristics(
                        "x86", "Linux", "Xen",
                        hostList, 10.0, 3.0,
                        0.05, 0.1, 0.1);

        Datacenter datacenter = null;

        try {
            datacenter = new Datacenter(
                    name,
                    characteristics,
                    new VmAllocationPolicySimple(hostList),
                    new LinkedList<Storage>(),
                    0);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return datacenter;
    }

    // Print Cloudlet Results
    private static void printCloudletList(List<Cloudlet> list) {

        String indent = "    ";
        DecimalFormat dft = new DecimalFormat("###.##");

        Log.printLine();
        Log.printLine("========== FCFS OUTPUT ==========");
        Log.printLine("Cloudlet ID" + indent
                + "STATUS" + indent
                + "VM ID" + indent
                + "Time" + indent
                + "Start Time" + indent
                + "Finish Time");

        for (Cloudlet cloudlet : list) {

            if (cloudlet.getCloudletStatus() == Cloudlet.SUCCESS) {
                Log.printLine(
                        cloudlet.getCloudletId() + indent
                        + "SUCCESS" + indent
                        + cloudlet.getVmId() + indent
                        + dft.format(cloudlet.getActualCPUTime()) + indent
                        + dft.format(cloudlet.getExecStartTime()) + indent
                        + dft.format(cloudlet.getFinishTime()));
            }
        }
    }
}
