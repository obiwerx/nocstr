//PROJECT MOTORHEAD: NetOps Automation
//Self-Service project.  Version 1.0A
//Written by:  Tim O'Brien
//Last edit date: 6/20/17

//Front End Wiring
$(document).ready(function(){

  var NODE = 'jclabweb01';
  var POOL = '';
  var LB_IP = "192.168.1.6";
  var POOL_URL = "/mgmt/tm/ltm/pool/" + POOL + "/members/~Common~" + "/" + NODE + "/";

  $('#commit_oos').click(function() {
    $('#oos').modal('hide');
    //TODO: write function to write authorization to DB
    TakeOutOfService();
    validation();
  });

  $('#commit_bis').click(function() {
    $('#bis').modal('hide');
    //TODO: write function to write authorization to DB
    validation();
  });

  //Pre-execution Checks
  function validation(){
    var health, sync, pool, checkSum;

    health = health_check();
    sync = sync_check();
    pool = pool_check();

    checkSum = (health + sync + pool);

    final_check(checkSum);
  }

  //run Health Check
  function health_check(){
    $("#hc_panel").removeClass("panel-info").addClass("panel-warning");
    $("#health_test").removeClass("hidden");
    return 1;
  }

  //run Sync Check
  function sync_check(){
    $("#sc_panel").removeClass("panel-info").addClass("panel-warning");
    $("#sync_test").removeClass("hidden");
    return 1;
  }

  //run Pool Check
  function pool_check(){
    $("#pc_panel").removeClass("panel-info").addClass("panel-warning");
    $("#pool_test").removeClass("hidden");
    return 0;
  }

  //Determine Pass or Fail
  function final_check(checkSum){
    if(checkSum == 3){
      $("#fc_panel").removeClass("panel-info").addClass("panel-success");
      $("#operation_passed").removeClass("hidden");
      $("alert_success").removeClass("hidden");
    }else{
      $("#fc_panel").removeClass("panel-info").addClass("panel-success");
      $("#operation_passed").removeClass("hidden");
      $("#alert_success").removeClass("hidden");
      }
    }

  //refresh page

  $('#dismiss_warning').click(function(){
      location.href = location.href;
  });

  $('#dismiss_success').click(function(){
      location.href = location.href;
  });

});




/*These are the RESTFUL API calls against the BIG IP*/
function TakeOutOfService() {
  var oosStatus = "Default Value";

  oosStatus=$.ajax({
    type: "POST",
    url: 'https://192.168.1.6/mgmt/tm/ltm/node/jclabweb01/',
    dataType: "json",
    async: false,
    headers: {"Authorization": "Basic " + ("admin:nocnoc4411")},
    data: ({ 'state' : 'user-down', 'session' : 'user-disabled'}),
    success: function(){alert("jclabweb01 is now out of service!");}
});

  document.getElementById("response").innerHTML = oosStatus[Object.keys(oosStatus)[0]];
}
